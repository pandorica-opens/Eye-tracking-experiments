#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

# Import key parts of the PsychoPy library:
from psychopy import visual, event, core
from psychopy import gui

from psychopy.core import getTime, wait 
from psychopy.data import importConditions
from psychopy.iohub import (EventConstants, EyeTrackerConstants,
                            getCurrentDateTimeString, ioHubExperimentRuntime)
import os
import random
import site

import os
import eventtxt
import subprocess
import csv
import time
import random

welcome_screen = 'welcome screen.PNG'

input_file_dir = 'Input_file.csv'
order_file_dir = 'order_input_file.csv'
output_file_dir = 'Exp Results\\'+'output_file.csv'
n_conditions = 8

points_in_euros = 0.014
showup_fee = 8.0
incentivation = 0.10



blank_screen_duration = 0.5 #in seconds...

code_table = {'0':'D', '1':'K', '2':'L', '3':'B', '4':'F', '5':'A', '6':'N', '7':'Q', '8':'X', '9':'E'}

class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    """
    
            
    def run(self,*args):
        
        from psychopy.iohub import module_directory
        
        exp_script_dir = module_directory(self.run)
        """
        The run method contains your experiment logic. It is equal to what would be in your main psychopy experiment
        script.py file in a standard psychopy experiment setup. That is all there is too it really.
        """

        def get_time():
            #get time in nice format to name the csv file
            localtime=time.asctime(time.localtime(time.time()))
            localtime=localtime[11:16]+'pm-'+localtime[4:10]
            localtime=localtime.replace(":","_").replace(" ","_")
            return localtime

        def empty_screen(win):
            
            text = visual.TextStim(win, text='*', height=40, units='pix', pos = [500, 430],color=[255,255,255],colorSpace='rgb255')
            
            text.draw()
            win.flip()
            
            event.waitKeys(keyList=['f2'])
            
        def read_input_file(csv_dir):
            data = []
            with open(csv_dir, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in spamreader:
                    data.append(row[0].split(","))
            return data

        def instruction_screen(win, img_name):
            
            img = visual.ImageStim(win, image=img_name, units='pix')
            img.draw()
            win.flip()
            k = event.waitKeys(keyList=['f2', 'right'])
            if k[0] == 'f2':
                win.close()
                core.quit()
            elif k[0] == 'right':
                pass

        def get_next_idx(current_idx, key):
            if key == 'right':
                if current_idx == 5: return 0
                else: return current_idx + 1
            else:
                if current_idx == 0: return 5
                else:
                    return current_idx -1


        def check_code_values(code_text):
            import string
            number_list = ['0','1','2','3','4','5','6','7','8','9']
            letter_list = list(string.ascii_lowercase) + ['*']
            
            messages = ''
            success = True

            if code_text[0] not in letter_list: 
                messages += 'Code 1 has to be letter.\n'
                success = False
            if code_text[1] not in letter_list:
                messages += 'Code 2 has to be letter.\n'
                success = False
            if code_text[2] not in letter_list:
                messages += 'Code 3 has to be letter.\n'
                success = False
            if code_text[3] not in letter_list:
                messages += 'Code 4 has to be letter.\n'
                success = False
            if code_text[4] not in number_list: 
                messages += 'Code 5 has to be number.\n'
                success = False
            if code_text[5] not in number_list:
                messages += 'Code 6 has to be numbder.\n'
                success = False
                
            return success, messages
            

        def trial_experiment(win, trial_data):
            
            for round_data in trial_data:
                
                
                round_results = do_round(win, round_data, is_trial=True)
                draw_payoff(win, round_data, round_results, trial_id=None)
                win.flip() 
                
            k = event.waitKeys(keyList=['f2', 'right'])
            if k[0] == 'f2':
                win.close()
                core.quit()
            elif k[0] == 'right':
                pass
                
        def experiment_begins(win):
            text = "Sie haben die Probedurchgänge nun abgeschlossen. Nun beginnt das eigentliche Experiment, welches auszahlungsrelevant wird. \nDer nächste Teil wird ca. 10 Minuten dauern. Sie können in diesen 10 Minuten keine Pausen einlegen.\
            \nFalls Sie noch Fragen haben, melden Sie sich bitte jetzt beim Experimentator.\n\nFalls Sie keine Fragen mehr haben, drücken Sie bitte die Pfeiltaste nach rechts, um das Experiment zu beginnen."
            
            text_obj = visual.TextStim(win, text=text, height=30, alignHoriz='center', units='pix', pos = [0,0],color=[255,255,255],colorSpace='rgb255', wrapWidth=win.size[0]*.7)
            text_obj.draw()
            win.flip()
            
            event.waitKeys(keyList=['right'])
            

        def main_experiment(win, main_data):
            experiment_results = []
            for round_data in main_data:

                
                round_results = do_round(win, round_data, False)
                
                experiment_results.append(round_results)
                win.flip() 
                time.sleep(0.5)
            
            selected_round_idx = random.randint(0, len(experiment_results)-1)
            selected_round_results = experiment_results[selected_round_idx]
            
            selected_round_data = []
            for round_data in main_data:
                if int(round_data[0]) == int(selected_round_results['picked_item']):
                    selected_round_data = round_data
                    
            draw_payoff(win, selected_round_data, selected_round_results, trial_id=selected_round_idx+1)
            to_output(subj_id, condition, exp_time, experiment_results, csv_experiment_output)
            k = event.waitKeys(keyList=['f2', 'up', 'down'])
            if k[0] == 'f2':
                win.close()
                core.quit()
            elif k[0] == 'up' or 'down':
                pass

        def to_output(subj_id, condition, localtime, results, output_file_dir):
            
            
            import os.path 
            is_exist = False
            if os.path.exists(output_file_dir): is_exist = True
            
            # Add header to the output file if it is the first time to write to it...
            if not is_exist:
                output_data_headers = ['trial', 'subject_id', 'condition', 'starting_time', 'item_picked', 
                'pressup', 'pressup_time', 'correct_answer']
                   
            # Python 2
            with open(output_file_dir, 'ab') as f:
            # Python 3
            #with open(output_file_dir, 'a', newline = '') as f:
               
                writer = csv.writer(f)
                if not is_exist:
                    writer.writerows([output_data_headers])
                
                for i in range(0, len(results)):
                    row = []
                    row.append(results[i]['pressup'])
                    row.append(results[i]['pressup_time'])
                    row.append(results[i]['correct_answer'])
                    
                    row.insert(0,str(i+1)) 
                    row.insert(1, str(subj_id))
                    row.insert(2, str(condition))
                    #row.insert(3, str(localtime)) #here you are actually outputing local time in the date format and not in the seconds
                    row.insert(3, str(localtime))
                    row.insert(4, results[i]['picked_item'])
                    #print('rows', row)
                    
                    writer.writerows([row])
                    
        def get_display_order(order_file_dir, condition):
            all_orders = []
            with open(order_file_dir, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                for row in spamreader:
                    
                    r = row[0].split(",")
                    all_orders.append(r)          
            
            return all_orders[int(condition[1])-1]
         
         
        def draw_screen(win, round_data, intervened, is_trial):
            global display_order
            global condition
            
            titles = ['Entscheider','Empfänger','Bestrafung','Ausgaben']
            
            if is_trial:
                Probedurchgang = visual.TextStim(win, text='Probedurchgang', pos = [0,400], units='pix', height=20,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.5)
                Probedurchgang.draw() 
            
            line = visual.Line(win, start=(-700, 0), end=(700, 0)) 

            # draw the tables
            tableA = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((-600, -50), (600, -50),(600, -430),(-600, -430), (-600, -50)),closeShape=False, pos=(0, 0), size=1)
            tableB = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((-600, -240), (600, -240)),closeShape=False, pos=(0, 0), size=1)
            tableC = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((0, -50), (0, -430)),closeShape=False, pos=(0, 0), size=1)

            label_1 = visual.TextStim(win, text=titles[int(display_order[0])-1], height=20, units='pix', pos = [-360,-150])
            label_2 = visual.TextStim(win, text=titles[int(display_order[1])-1], height=20, units='pix', pos = [-360,-350])
            label_3 = visual.TextStim(win, text=titles[int(display_order[2])-1], height=20, units='pix', pos = [360,-150])
            label_4 = visual.TextStim(win, text=titles[int(display_order[3])-1], height=20, units='pix', pos = [360,-350])
            
            number_1 = visual.TextStim(win, text=round_data[int(display_order[0])], height=20, units='pix', pos = [-120,-150])
            number_2 = visual.TextStim(win, text=round_data[int(display_order[1])], height=20, units='pix', pos = [-120,-350])
            number_3 = visual.TextStim(win, text=round_data[int(display_order[2])], height=20, units='pix', pos = [120,-150])
            number_4 = visual.TextStim(win, text=round_data[int(display_order[3])], height=20, units='pix', pos = [120,-350])
            
            
                
            line.draw()
            tableB.draw()
            tableC.draw()
            label_1.draw()
            label_2.draw()
            label_3.draw()
            label_4.draw()
            number_1.draw()
            number_2.draw()
            number_3.draw()
            number_4.draw()
            
            win.flip()

        def fixation_cross(win):
            fix = visual.TextStim(win, text='+', pos = [0,0], height=60,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.5)
            fix.draw()
            win.flip()
            
        def do_round(win, round_data, is_trial):

            global display_order
            global condition
            
            pressup = 0
            correct_answer = 0
            print('round_data', round_data, 'is trial', is_trial)
            
            results = {'correct_answer':[], 'picked_item':round_data[0], 'points':0., 'pressup':'0', 'pressup_time':'99'}
            
            results['correct_answer'] = '0'
            
            clock = core.Clock()
            draw_screen(win, round_data, pressup, is_trial)
            e=event.waitKeys(keyList=['up', 'down','f2'])
            print('get into len(e) > 0 if', e)
            
            self.hub.clearEvents('all')
            if len(e)>0:
                print('get into len(e) > 0 if', e, len(e))
                if e[0] in ['up'] and not pressup:
                    pressup = 1
                    results['pressup'] = '1'
                    results['pressup_time'] = getTime()
                    #results['pressup_time'] = round(clock.getTime(), 2)
                    
                elif e[0] in ['down'] and not pressup:
                    pressup = 0
                    results['pressup'] = '0'
                    #results['pressup_time'] = round(clock.getTime(), 2)
                    results['pressup_time'] = getTime()
                
                #print('round data 9', round_data[13])
                if e[0] == 'up' and round_data[13] == '1': 
                    # up is '1' in the input file, hence when we have '1' in the input and up it is correct_answer
                    # if it is '0' and down -: false
                    correct_answer = 1
                    results['correct_answer'] = '1'
                    results['points'] = 0.1
                
                elif e[0] == 'down' and round_data[13] == '0':
                    correct_answer = 1
                    results['correct_answer'] = '1'
                    results['points'] = 0.1
                    
                draw_screen(win, round_data, pressup, is_trial)
            
            print(results)
            
            #here we enforce to continue despite pressing the key, I have commented it out so you can remember what you were doing here
            #k = event.waitKeys(keyList=['f2', 'up', 'down'])
            if e[0] == 'f2':
                win.close()
                core.quit()
            #if k[0] == 'f2':
            #    win.close()
            #    core.quit()
            #elif k[0] == ['up','down']:
            #    pass
            return results

        def draw_payoff(win, selected_round_data, selected_round_results, trial_id=None):
            global display_order
            correct_answer_points = int(selected_round_data[4])
                
            if not trial_id:
                Probedurchgang = visual.TextStim(win, text='Probedurchgang', pos = [0,400], units='pix', height=20,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.5)
                Probedurchgang.draw() 

                if selected_round_results['correct_answer'] == '0':
                    payoff_text_1 = "Sie haben in dieser Runde falsch entschieden.\n\nSie erhalten daher kein Geld für diese Runde.\n"
                else:
                    payoff_text_1 = "Sie haben in dieser Runde richtig entschieden. \n\nSie erhielten daher 0,10€ zusätzlich für diesen Durchgang."
                
                payoff_text_1_obj = visual.TextStim(win, text=payoff_text_1, height=25, units='pix', pos = [0,250], wrapWidth=win.size[0]*.7, alignHoriz='center')
                payoff_text_1_obj.draw()

                continue_text = "Bitte drücken Sie die Pfeiltaste nach rechts (-->)"
                continue_text_obj = visual.TextStim(win, text=continue_text, height=25, units='pix', pos = [0,50], wrapWidth=win.size[0]*.7, alignHoriz='center')
                continue_text_obj.draw()
                
            # draw the tables
            titles = ['Entscheider','Empfänger','Bestrafung','Ausgaben']
            
            tableA = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((-600, -50), (600, -50),(600, -430),(-600, -430), (-600, -50)),closeShape=False, pos=(0, 0), size=1)
            tableB = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((-600, -240), (600, -240)),closeShape=False, pos=(0, 0), size=1)
            tableC = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((0, -50), (0, -430)),closeShape=False, pos=(0, 0), size=1)

            label_1 = visual.TextStim(win, text=titles[int(display_order[0])-1], height=20, units='pix', pos = [-360,-150])
            label_2 = visual.TextStim(win, text=titles[int(display_order[1])-1], height=20, units='pix', pos = [-360,-350])
            label_3 = visual.TextStim(win, text=titles[int(display_order[2])-1], height=20, units='pix', pos = [360,-150])
            label_4 = visual.TextStim(win, text=titles[int(display_order[3])-1], height=20, units='pix', pos = [360,-350])
            
            number_1 = visual.TextStim(win, text=selected_round_data[int(display_order[0])], height=20, units='pix', pos = [-120,-150])
            number_2 = visual.TextStim(win, text=selected_round_data[int(display_order[1])], height=20, units='pix', pos = [-120,-350])
            number_3 = visual.TextStim(win, text=selected_round_data[int(display_order[2])], height=20, units='pix', pos = [120,-150])
            number_4 = visual.TextStim(win, text=selected_round_data[int(display_order[3])], height=20, units='pix', pos = [120,-350])
            

            line = visual.Line(win, start=(-700, 0), end=(700, 0)) 


            
            tableB.draw()
            tableC.draw()
            label_1.draw()
            label_2.draw()
            label_3.draw()
            label_4.draw()
            number_1.draw()
            number_2.draw()
            number_3.draw()
            number_4.draw()
            line.draw()
            
            win.flip()        
            
            k = event.waitKeys(keyList=['f2', 'right'])
            if k[0] == 'f2':
                win.close()
                core.quit()
            elif k[0] == 'right':
                pass
            
        def calculate_code(win, payoff):
            
            text = "Thank you for partification! During 30 trials you solved " + str(payoff) + ' trials correctly, which means you will recieve ' + str(payoff*0.10)+ 'euro for your performance in task.'
            text_obj = visual.TextStim(win, text=text, height=20, pos = [0, 200], units='pix', wrapWidth=win.size[0]*.7, alignHoriz='center')
            text_obj.draw()
            win.flip()
            
        #****************Collect Information about the Subject****************************
        
        selected_eyetracker_name=args[0]
        
        # Let's make some short-cuts to the devices we will be using in this 'experiment'.
        tracker=self.hub.devices.tracker
        display=self.hub.devices.display
        kb=self.hub.devices.keyboard
        mouse=self.hub.devices.mouse
        
        # Start by running the eye tracker default setup procedure.
        tracker.runSetupProcedure()

        # Create a psychopy window, full screen resolution, full screen mode...
        display_coord_type=display.getCoordinateType()
        display_resolution=display.getPixelResolution()
        
       
        # it is recommended to use pixle as unit espically if you are using eye tracker, because the eyetracker returns the readings in pixel
        win=visual.Window(display_resolution,monitor=display.getPsychopyMonitorName(),units='pix',fullscr=True,screen= display.getIndex(),
        waitBlanking=False) #color="white"
        
        # Hide the 'system mouse cursor'.
        # would need it for later
        mouse.setSystemCursorVisibility(False)
        event.Mouse(visible=False)
        
        

        
        #------------------------------------------------------------Experiment begins ----------------------------------------------------------------------------------------------
        
        #get time in nice format to name the csv file
        localtime=time.asctime(time.localtime(time.time()))
        localtime=localtime[11:16]+'pm-'+localtime[4:10]
        localtime=localtime.replace(":","_").replace(" ","_")
        
        
        tracker.setRecordingState(True)
        
        
        global order_file_dir, input_file_dir, output_file_dir, subj_id, condition, csv_experiment_output
        
        
        #subj_id, condition = get_subject_info()
        exp_dir = os.getcwd()
                
        exp_time=get_time()
        
        #create csv file
        csv_eye_output='Exp Results\\'+subj_id+'_eyetracking_output'+localtime+'.csv'
        csv_experiment_output ='Exp Results\\'+subj_id+'_decision_output'+localtime+'.csv'


        order_file_dir = exp_dir+'\\'+order_file_dir
        input_file_dir = exp_dir+'\\'+input_file_dir
        output_file_dir = exp_dir+'\\'+output_file_dir


        # Create a psychopy window, full screen resolution, full screen mode...
        win=visual.Window(fullscr = True)
        
        # Waiting for the user to press F2
        empty_screen(win)

        #**********************************instructions_text start*************************************
        
        instruction_screen(win, welcome_screen)
            

        #**********************************Reading Data**************************************
        # get order of display...
        global display_order
        display_order = get_display_order(order_file_dir, condition)
        

        # get data...
        all_data = read_input_file(input_file_dir) 
        trial_data = all_data[1:4]

        fixed_data = all_data[4:9]
        shuffled_data = all_data[9:]
        random.shuffle(shuffled_data)
        main_data = fixed_data + shuffled_data

        trial_experiment(win, trial_data)
        experiment_begins(win)

        #------------------------------------------------------------ Main Experiment Starts ----------------------------------------------------------------------------------------------

        experiment_results = []
        t = 0
        sum_correct = 0
        for round_data in main_data:
            t += 1
            flip_time=win.flip()
            
            time.sleep(0.5)
            
            round_results = do_round(win, round_data, is_trial = False)
            sum_correct = sum_correct + int(round_results['correct_answer'])
            
            experiment_results.append(round_results)
            
            
            win.flip()

            flip_time=win.flip()
            
        print('sum', sum_correct)
        to_output(subj_id, condition, exp_time, experiment_results, csv_experiment_output)
                     
        #------------------------------------------------------------ Main Experiment Ends ----------------------------------------------------------------------------------------------
                       
        #================= Draw Last Screen (Payoff) ==================
        selected_round_idx = random.randint(0, len(experiment_results)-1)
        selected_round_results = experiment_results[selected_round_idx]
                        
        selected_round_data = []
        for round_data in main_data:
            #print(round_data[0], selected_round_results['picked_item'])
            if int(round_data[0]) == int(selected_round_results['picked_item']):
                selected_round_data = round_data
                                
        draw_payoff(win, selected_round_data, selected_round_results, trial_id=selected_round_idx+1)
        calculate_code(win, sum_correct)
        
        event.waitKeys(keyList=['f2'])
        
        #------------------------------------------------------------Experiment ends ----------------------------------------------------------------------------------------------

        # Disconnect the eye tracking device.
           
        # So the experiment is done, all trials have been run.
        # Clear the screen and show an 'experiment  done' message using the
        # instructionScreen state. What for the trigger to exit that state.
        # (i.e. the space key was pressed)
        #
        flip_time=win.flip()
        self.hub.sendMessageEvent(text='EXPERIMENT_COMPLETE',sec_time=flip_time)
        tracker.setRecordingState(False)
        tracker.setConnectionState(False)
        
        self.hub.sendMessageEvent(text="SHOW_DONE_TEXT")
        print("SHOW_DONE_TEXT")

        tex1=eventtxt.Eventtotext()
        print('tex1=eventtxt.Eventtotext()', tex1)
        #use try: would give an error in case of the not connected eye tracker at later stages
        tex1.convertToText(exp_script_dir,subj_id,localtime)
        self.hub.clearEvents('all')
        #self.hub.clearEvents('all', exp_script_dir) 
        
        # MANAGER ERROR WHEN SENDING MSG:[Errno 9] Bad file descriptor
        #Warning: TimeoutExpired, Killing ioHub Server process.
        
        #ioHubExperimentRuntime.shutdown()
        print('ioHubExperimentRuntime')
        win.close()
        self.hub.quit()
        print('end of exp logic')
        
        
        ### End of experiment logic
        
    
    
    
    
        
####### Main  #######
if __name__ == "__main__":
    
    import os
    from psychopy import gui
    from psychopy.iohub import module_directory

    def main(configurationDirectory):
        """
        Creates an instance of the ExperimentRuntime class, gets the eye tracker
        the user wants to use for the demo, and launches the experiment logic.
        """
        # The following code merges a iohub_config file called iohub_config.yaml.part,
        # that has all the iohub_config settings, other than those for the eye tracker.
        # the eye tracker configs are in the yaml files in the eyetracker_configs dir.
        #
        # This code lets a person select an eye tracker, and then merges the main iohub_config.yaml.part
        # with the contents of the eyetracker config yaml in eyetracker_configs
        # associated with the selected tracker.
        #
        # The merged result is saved as iohub_config.yaml so it can be picked up
        # by the Experiment _runtime
        # as normal.
        
        eye_tracker_config_files={
                                  'LC Technologies EyeGaze':'eyetracker_configs/eyegaze_config.yaml',
                                  'SMI iViewX':'eyetracker_configs/iviewx_config.yaml',
                                  'The Eye Tribe':'eyetracker_configs/iTribe_config.yaml'
                                  }

        info = {'Eye Tracker Type': ['Select', 'LC Technologies EyeGaze','The Eye Tribe',
                                     'SMI iViewX']}

        dlg_info=dict(info)
        infoDlg = gui.DlgFromDict(dictionary=dlg_info, title='Select Eye Tracker')
        if not infoDlg.OK:
            return -1

        while dlg_info.values()[0] == u'Select' and infoDlg.OK:
                dlg_info=dict(info)
                infoDlg = gui.DlgFromDict(dictionary=dlg_info, title='SELECT Eye Tracker To Continue...')

        if not infoDlg.OK:
            return -1


        #****************Collect Information about the Subject****************************
        
        global subj_id,condition
        
        order_list=range(1,25)
        info = {'Subject_ID':000,'Condition':[]}
        for i in xrange(1, n_conditions+1):
            info['Condition'].append('1'+str(i))

                
        infoDlg = gui.DlgFromDict(dictionary=info, title='Das Experiment',order=['Subject_ID','Condition'])
        if infoDlg.OK: #this will be True (user hit OK) or False (cancelled)
            subj_id=str(info['Subject_ID'])
            condition=str(info['Condition'])

        else:
            core.quit()
            
        if os.path.isfile(configurationDirectory+"\events.hdf5"):
            os.remove(configurationDirectory+"\events.hdf5")

        #****************Run calibration for eyetibe****************************
        if dlg_info.values()[0] =='The Eye Tribe':
            s=subprocess.Popen(["C:\Program Files (x86)\EyeTribe\Server\EyeTribe.exe"],stdout=subprocess.PIPE)
            time.sleep(5.0)
            p=subprocess.Popen(["C:\Program Files (x86)\EyeTribe\Client\EyeTribeUIWin.exe"],stdout=subprocess.PIPE)
            count=0
            fails_counter = 0
            point_counter=0
            
            accepted = True
            #uncomment in case of calibration
            
            ''' while True:
                line=p.stdout.readline()
                
                print line
                print fails_counter, point_counter
                
                if 'Recal' in line: 
                    accepted = False
                    
                
                if '- - P('in line or 'PointStart' in line:
                    if accepted:
                        point_counter+=1
                    else:
                        accepted = True
                        point_counter+=1
                
                if accepted and "CalibrationResult" in line:
                #if "CalibrationResult" in line:
                    line=line.replace(",", ".")
                    avg=float(line[line.index("avg")+5:line.index("left")-1])
                    left=float(line[line.index("left")+6:line.index("right")-1])
                    right=float(line[line.index("right")+7:len(line)-2])
                    
                    if avg<0.8 and avg!=0 and left<0.8 and left!=0 and right<0.8 and right!=0 and point_counter>=9:
                        break
                        # the value 0.4 represent the tolerance with the calibration, it is proportional relation 
                    elif point_counter>=9:
                        point_counter=0
                        fails_counter += 1
                        
                        dlg = gui.Dlg(title="Calibration")
                        dlg.addText('Please Re_calibrate', color='red')
                        dlg.show()
                
                if not accepted and "CalibrationResult" in line: accepted = True
                
                if fails_counter == 3: 
                    global calibration_failed
                    calibration_failed = 1
                    break'''
        
        base_config_file=os.path.normcase(os.path.join(configurationDirectory,
                                                       'iohub_config.yaml.part'))

        eyetrack_config_file=os.path.normcase(os.path.join(configurationDirectory,
                                eye_tracker_config_files[dlg_info.values()[0]]))

        combined_config_file_name=os.path.normcase(os.path.join(configurationDirectory,
                                                                'iohub_config.yaml'))

        ExperimentRuntime.mergeConfigurationFiles(base_config_file,
                                eyetrack_config_file,combined_config_file_name)


        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")
        #print('after runtime')
        runtime.start((dlg_info.values()[0],))
        #print('after runtime info ')
        os.remove(configurationDirectory+"\events.hdf5")#this line to remove the hdf5 so in the next run of the expermint will not append
        #print('after remove')
        
        '''if dlg_info.values()[0] =='The Eye Tribe':
            #s.terminate() WindowsError: [Error 5] Zugriff verweigert

            p.terminate()'''
        print('after terminate s,p')
        
   
        
    # Get the current directory, using a method that does not rely on __FILE__
    # or the accuracy of the value of __FILE__.
    #
    configurationDirectory=module_directory(main)

    # Run the main function, which starts the experiment runtime
    #
    main(configurationDirectory) 
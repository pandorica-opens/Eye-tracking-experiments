# -*- coding: utf-8 -*-
"""
eye_tracker/run.py

Demonstrates the ioHub Common EyeTracking Interface by displaying a gaze cursor
at the currently reported gaze position on an image background.
All currently supported Eye Tracker Implementations are supported,
with the Eye Tracker Technology chosen at the start of the demo via a
drop down list. Exact same demo script is used regardless of the
Eye Tracker hardware used.

Inital Version: May 6th, 2013, Sol Simpson
"""
from psychopy import visual, event,core, logging
from psychopy.data import TrialHandler,importConditions
from psychopy.iohub import (EventConstants, EyeTrackerConstants,
                            getCurrentDateTimeString, ioHubExperimentRuntime)
import os
import random
import site
site.addsitedir('C:\Python27\Lib\site-packages')
from psynteract import Connection 
import psynteract
import socket
import csv
import eventtxt
import subprocess
import time
import math


subj_id=-1
con=1
calibration_failed = 0

input_file_2_dir = 'input.csv'
output_file_2_dir_decision = 'Exp Results\\output_decision.csv'
output_file_2_dir_eyetracking = 'Exp Results\\output_eyetracking.csv'
#logfile = logging.LogFile(f= 'Error Results.txt', level = 30, filemode = 'a', logger = None, encoding = 'utf8') #not working


class ExperimentRuntime(ioHubExperimentRuntime):
    """
    Create an experiment using psychopy and the ioHub framework by extending the ioHubExperimentRuntime class. At minimum
    all that is needed in the __init__ for the new class, here called ExperimentRuntime, is the a call to the
    ioHubExperimentRuntime __init__ itself.
    """
    
            
    def run(self,*args):
        
        """
        The run method contains your experiment logic. It is equal to what would be in your main psychopy experiment
        script.py file in a standard psychopy experiment setup. That is all there is too it really.
        """
        global subj_id
        global con
        
        from psychopy.iohub import module_directory
        exp_script_dir = module_directory(self.run)
        exp_conditions = importConditions(os.path.join(exp_script_dir,
                                                       'trial_conditions.xlsx'))
                                                       
        trials = TrialHandler(exp_conditions, 1)
        
        #Use Esc to quit, it will be called at some stages during the experiment
        def _checkQuit(key):
            if key[0]=='escape':
                os._exit(1)
                core.quit()
        
        ###########
        #### Fiona's experiment functions
        ###########
        def to_output(subject_id, decision, trigger, inputcsv):

            global output_file_2_dir    

            import os.path 

            is_exist = False
            if os.path.exists(output_file_2_dir): is_exist = True

            # Add header to the output file if it is the first time to write to it...
            if not is_exist:    
                output_data_headers = ['Subject_id', 'Decision', 'Trigger', 'Inputcsv']
                      

            # Python 2
            with open(output_file_2_dir, 'ab') as f:

            # Python 3
            #with open(output_file_dir, 'a', newline = '') as f:

                writer = csv.writer(f)
                if not is_exist:
                    writer.writerows([output_data_headers])
                
                writer.writerows([[subject_id, decision, trigger, inputcsv]])

        def instructions(win):

            #change to the right instructions
            inst_dir = 'Instructions\Inst_2.jpg'
            

            instr=visual.ImageStim(win,image=inst_dir, units='norm', size=(1.5, 1.5))
            instr.draw()
            win.flip()
            event.waitKeys(keyList=['space']) 
        
        def read_input_file(csv_dir):
    
            global subj_id
            
            with open(csv_dir, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter='\n', quotechar='|')
               
                for row in spamreader:
                    if row[0].split(",")[6] == str(subj_id):  #why subj id
                        return row[0].split(',')

    
        def draw_decision_screen(win, tracker, trigger, entscheider, empfanger, eingreifen, kosten, bestrafung):
            
            text = psychopy.visual.TextStim(
                            win=win,
                            text="Hello, world!",
                            color=[-1, -1, -1])
                            
            text.draw()
    
            flip_time=win.flip()
            
            return 0
           
        
        ###########
        #### Susa's experiment functions
        ###########
        
        
        def fill_row(csv_opject,subj_id,partner_ID,trial,my_role,decision_list,key,partner_data,condition):

            #log file data
            decision_A=decision_list[1:3]
            decision_B=decision_list[5:7]
            item_num=decision_list[0]
            

            if key[0]=='m':
                proposer_choice=0
            elif key[0]=='c':
                proposer_choice=1
                
            if partner_data:
                responder_accept="1"
            else:
                responder_accept="0"
                
             
            #filling up the rows
            writer=csv_opject
            writer.writerow({'trial':trial+1,'subject':subj_id,'partner':partner_ID,'item':item_num,'Role':my_role,'Condition':str(condition),'A_self':decision_A[0],'A_other':decision_A[1],'B_self':decision_B[0],'B_other':decision_B[1],
            'Choice_A':proposer_choice,'Choice_accept':responder_accept})
            
         
        def choose_proposal(win,list,order):
    
            text_list=['Ihre Auszahlung','Die Auszahlung des anderen','Auszahlungsdifferenz','Summe der Auszahlung']
    
            optionA = visual.TextStim(win, text='A', pos = [-150,380], height=20,color=[255,255,255],colorSpace='rgb255')#lable A
            optionB = visual.TextStim(win, text='B', pos = [150,380], height=20,color=[255,255,255],colorSpace='rgb255')#lable B
            line1= visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((0, 275), (-450, 275),(-450, -400),(0, -400)),closeShape=False, pos=(0, 0), size=1)
            line2= visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((0, 275), (450, 275),(450, -400),(0, -400)),closeShape=False, pos=(0, 0), size=1)
            line3= visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((0, 275), (0,-400)),closeShape=False, pos=(0, 0), size=1)
            text1 = visual.TextStim(win, text=text_list[int(order[0])], pos = [-600,200], height=15,color=[255,255,255],colorSpace='rgb255')#first numer left_top
            text2 = visual.TextStim(win, text=text_list[int(order[1])], pos = [-600,50], height=15,color=[255,255,255],colorSpace='rgb255')#second num left_down
            text3 = visual.TextStim(win, text=text_list[int(order[2])], pos = [-600,-100], height=15,color=[255,255,255],colorSpace='rgb255')#third num right top
            text4 = visual.TextStim(win, text=text_list[int(order[3])], pos = [-600,-250], height=15,color=[255,255,255],colorSpace='rgb255')#third num right down
            
            num1 = visual.TextStim(win, text=list[int(order[0])+1], pos = [-150,200], height=15,color=[255,255,255],colorSpace='rgb255')#first numer left_top
            num2 = visual.TextStim(win, text=list[int(order[1])+1], pos = [-350,50], height=15,color=[255,255,255],colorSpace='rgb255')#second num left_down
            num3 = visual.TextStim(win, text=list[int(order[2])+1], pos = [-150,-100], height=15,color=[255,255,255],colorSpace='rgb255')#third num right top
            num4 = visual.TextStim(win, text=list[int(order[3])+1], pos = [-350,-250], height=15,color=[255,255,255],colorSpace='rgb255')#third num right down
            num5 = visual.TextStim(win, text=list[int(order[0])+1+4], pos = [150,200], height=15,color=[255,255,255],colorSpace='rgb255')#third num right top
            num6 = visual.TextStim(win, text=list[int(order[1])+1+4], pos = [350,50], height=15,color=[255,255,255],colorSpace='rgb255')#third num right down
            num7 = visual.TextStim(win, text=list[int(order[2])+1+4], pos = [150,-100], height=15,color=[255,255,255],colorSpace='rgb255')#third num right top
            num8 = visual.TextStim(win, text=list[int(order[3])+1+4], pos = [350,-250], height=15,color=[255,255,255],colorSpace='rgb255')#third num right down
            
            optionA.draw()
            optionB.draw()
            #draw the lins
            line1.draw()
            line2.draw()
            line3.draw()
            #draw the number
            num1.draw()
            num2.draw()
            num3.draw()
            num4.draw()
            num5.draw()
            num6.draw()
            num7.draw()
            num8.draw()
            #draw the text
            text1.draw()
            text2.draw()
            text3.draw()
            text4.draw()

            win.flip()
            key=event.waitKeys(keyList=['c','m'])
            if key[0]=='c':
                line1.lineColor=(230,240,60)
                line3.lineColor=(230,240,60)
                line1.draw()
                line3.draw()
            else:
                line2.lineColor=(230,240,60)
                line3.lineColor=(230,240,60)
                line2.draw()
                line3.draw()
                
            optionA.draw()
            optionB.draw()
            line1.draw()
            line2.draw()
            line3.draw()
            num1.draw()
            num2.draw()
            num3.draw()
            num4.draw()
            num5.draw()
            num6.draw()
            num7.draw()
            num8.draw()
            #draw the text
            text1.draw()
            text2.draw()
            text3.draw()
            text4.draw()
            
            win.flip()
            time.sleep(0.3)
            return key
            
            

        # Inform the ioDataStore that the experiment is using ac
        # TrialHandler. The ioDataStore will create a table
        # which can be used to record the actual trial variable values (DV or IV)
        # in the order run / collected.
        #
        self.hub.createTrialHandlerRecordTable(trials)

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
        win=visual.Window(display_resolution,monitor=display.getPsychopyMonitorName(),units='pix',fullscr=True,screen= display.getIndex())
        
        # Hide the 'system mouse cursor'.
        mouse.setSystemCursorVisibility(False)
        event.Mouse(visible=False)

        inst1=visual.ImageStim(win,pos=(0,0))
        inst2=visual.ImageStim(win,pos=(0,0))
        fixation_cross = visual.TextStim(win, text='+', pos = [0,0], height=54,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)

        message1 = visual.TextStim(win, text='Die Studie beginnt in Kürze.', pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        message1_p=visual.TextStim(win, text='Bitte warten Sie auf die Entscheidung des anderen Spielers', pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        message2_p = visual.TextStim(win, pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        message1_r = visual.TextStim(win, text='Bitte warten Sie auf die Entscheidung des anderen Spielers.', pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        message2_r = visual.TextStim(win, text='Bitte warten Sie auf die Entscheidung des anderen Spielers.', pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        
        messages = [message1, message1_p, message2_p, message1_r, message2_r]
        
        #all possible permutations for order variable (instead of using if statment)
        permutations={1: '0123', 2: '0132',3: '0213', 4: '0231',5:'0312' , 6: '0321',
                      7: '1023', 8: '1032',9: '1203', 10: '1230',11: '1302',12: '1320',
                     13:'2013', 14: '2031',15:'2103',16:'2130',17:'2301',18:'2310',
                     19:'3012',20:'3021',21:'3102', 22:'3120',23:'3201', 24: '3210'}
                     
        order=permutations[con]
        
        
        
        
        
        #------------------------------------------------------------Trial Example starts ----------------------------------------------------------------------------------------------
        
        #get time in nice format to name the csv file
        localtime=time.asctime(time.localtime(time.time()))
        localtime=localtime[11:16]+'pm-'+localtime[4:10]
        localtime=localtime.replace(":","_").replace(" ","_")
        
        #create csv file
        csv_name='Exp Results\\'+subj_id+'_Example_info'+localtime+'.csv'
        
        #define the columns 
        fieldnames = ['trial','subject','partner','Role','item','Condition','A_self','A_other','B_self','B_other','Choice_A','Choice_accept']
        
        

        
        
        #variables
        inst.image = 'Instructions\Inst.png'
        inst2.image = 'Instructions\Inst_2.png'
    
        prop_data=get_proposals_data('prop_data.csv')
        example_prop_data = [prop_data[0]]
        item_list=range(0,len(example_prop_data))
        n_example_trial = len(example_prop_data)

        
        
        inst.draw()
        win.flip()
        key=event.waitKeys(keyList=['space'])
        inst2.draw()
        win.flip()
        key=event.waitKeys(keyList=['space'])
        
       
        #show example message
        example_message = visual.TextStim(win, text="Probedurchgang (dieser wird nicht relevant für Ihre spätere Auszahlung)", pos = [0,0], height=30,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.7)
        example_message.draw()
        win.flip()
        core.wait(5)

                            
        ### Show an example of 3 trials ...
        def do_example_trial(win, connection, t, writer,subj_id,partner_ID, my_role, prop_data, item_list, order, messages):
            # So request to start trial has occurred...
            # Clear the screen, start recording eye data, and clear all events
            # received to far.
            
            message1 = messages[0]
            message1_p = messages[1]
            message2_p = messages[2]
            message1_r = messages[3]
            message2_r = messages[4]
             
            
            if my_role=='proposer':
                #show Blank screen////////////triger 1
                win.flip()
                
                #select an item randomly from the CSV file with no replacment
                random.shuffle(item_list)
                item=item_list[0]
                del item_list[0]
                
                #select a proposal and send it to the partner//////////////triger 3
                key=choose_proposal(win,prop_data[item],order)
                send=prop_data[item]+key
                connection.data['example_choice'].append(send) # send selection to the DB
                connection.push()
                
                #show message//////////////////triger 9
                message1_p.draw()
                win.flip()
                
                #wait for the responder to reject/accept
                connection.data['example_response'].append(' ') # send selection to the DB
                connection.push()
                
                while True:
                    if len(connection.get(partner)['data']['example_response']) > t:
                        
                        break
              
                #connection.wait(lambda doc: len(doc['data']['example_response'])>(t),check='partner')
               
                partner_data=connection.get(partner)['data']['example_response'][-1]
                
                '''
                #show message//////////////////triger 4
                if partner_data:
                    message2_p.text="Ihre Entscheidung wurde vom anderen Spieler akzeptiert."
                else:
                    message2_p.text="Ihre Entscheidung wurde vom anderen Spieler abgelehnt."
                message2_p.draw()
                win.flip()
                time.sleep(2)
                '''
                
                #log file data
                fill_row(writer,subj_id,partner_ID,t,my_role,prop_data[item],key,partner_data,order)
          
            elif my_role=='responder':
                #wait till the partner send the propsel/////////////////triger 9
                message1_r.draw()
                win.flip()
                
                #show Blank screen////////// triger 1
                win.flip()
                time.sleep(0.5)
                
                
                
                #log file data partner_data looks like [nu1,nu2,nu3,nu4,c/m]
                fill_row(writer,subj_id,partner_ID,t,my_role,partner_data[:-1],partner_data[-1:],accept,order)

        for t in range(0,n_example_trial):
            do_example_trial(win, c, t, writer,subj_id,partner_ID, my_role, example_prop_data, item_list, order, messages)
        
        key=event.waitKeys(keyList=['space'])
        
        #------------------------------------------------------------Trial Example ends ----------------------------------------------------------------------------------------------
        
        
        
        
        
        #------------------------------------------------------------Trial Logic starts ----------------------------------------------------------------------------------------------
        
        #------------------------------------------------------------Trial Logic ends ----------------------------------------------------------------------------------------------
        
        
            
        
        # Disconnect the eye tracking device.
        #
        tracker.setConnectionState(False)
        
        
        flip_time=win.flip()
        self.hub.sendMessageEvent(text="SHOW_DONE_TEXT",sec_time=flip_time)

        cs.close()
        
           
        # So the experiment is done, all trials have been run.
        # Clear the screen and show an 'experiment  done' message using the
        # instructionScreen state. What for the trigger to exit that state.
        # (i.e. the space key was pressed)
        #
        self.hub.sendMessageEvent(text='EXPERIMENT_COMPLETE')
        tex1=eventtxt.Eventtotext()
        tex1.convertToText(exp_script_dir,subj_id,localtime)
        
        ### End of experiment logic
        

####### Main Script Launching Code Below #######

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
        global subj_id
        global con
        
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
        info = {'Subject_ID':000,'Condition':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]}
        infoDlg = gui.DlgFromDict(dictionary=info, title='MPI Experiment',order=['Subject_ID','Condition'])#this attribute can't be changed by the user
        if infoDlg.OK: #this will be True (user hit OK) or False (cancelled)
            subj_id=str(info['Subject_ID'])
            con=int(info['Condition'])
        else: 
            return -1
            
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
            '''while True:
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
                    break '''      
        
        base_config_file=os.path.normcase(os.path.join(configurationDirectory,
                                                       'iohub_config.yaml.part'))

        eyetrack_config_file=os.path.normcase(os.path.join(configurationDirectory,
                                eye_tracker_config_files[dlg_info.values()[0]]))

        combined_config_file_name=os.path.normcase(os.path.join(configurationDirectory,
                                                                'iohub_config.yaml'))

        ExperimentRuntime.mergeConfigurationFiles(base_config_file,
                                eyetrack_config_file,combined_config_file_name)


        runtime=ExperimentRuntime(configurationDirectory, "experiment_config.yaml")
        runtime.start((dlg_info.values()[0],))
        os.remove(configurationDirectory+"\events.hdf5")#this line to remove the hdf5 so in the next run of the expermint will not append
        
        if dlg_info.values()[0] =='The Eye Tribe':
            s.terminate()
            p.terminate()
        

    # Get the current directory, using a method that does not rely on __FILE__
    # or the accuracy of the value of __FILE__.
    #
    configurationDirectory=module_directory(main)

    # Run the main function, which starts the experiment runtime
    #
    main(configurationDirectory)

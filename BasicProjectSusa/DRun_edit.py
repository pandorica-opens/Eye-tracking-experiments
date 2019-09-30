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

input_file_2_dir = 'input_file_player_a_b.csv'
output_file_2_dir = 'Exp Results\\output_file_player_a_b.csv'
logfile = logging.LogFile(f= 'Error Results.txt', level = 30, filemode = 'a', logger = None, encoding = 'utf8') #not working


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
        def to_output_2(subject_id, decision):

            global output_file_2_dir    

            import os.path 

            is_exist = False
            if os.path.exists(output_file_2_dir): is_exist = True

            # Add header to the output file if it is the first time to write to it...
            if not is_exist:    
                output_data_headers = ['Subject_id', 'Decision']
                      

            # Python 2
            with open(output_file_2_dir, 'ab') as f:

            # Python 3
            #with open(output_file_dir, 'a', newline = '') as f:

                writer = csv.writer(f)
                if not is_exist:
                    writer.writerows([output_data_headers])
                
                writer.writerows([[subject_id, decision]])

        def instructions_2(win):

            inst_dir = 'Instructions\Inst_2.jpg'

            instr=visual.ImageStim(win,image=inst_dir, units='norm', size=(1.5, 1.5))
            instr.draw()
            win.flip()
            event.waitKeys(keyList=['space']) 
        
        def read_input_file_2(csv_dir):
    
            global subj_id
            
            with open(csv_dir, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter='\n', quotechar='|')
               
                for row in spamreader:
                    if row[0].split(",")[6] == str(subj_id):
                        return row[0].split(',')
        
        
            
    
        def draw1_player_ab(win, tracker, trigger):
    
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_START",sec_time=flip_time)
            self.hub.clearEvents('all')
            tracker.setRecordingState(True)
            
            tracker.setTriggerValue(trigger)
            
            
            text_decision = visual.TextStim(win, text='Bitte entscheiden Sie sich für Option A oder B.', pos=(0, 400), height=20, units='pix', color=[255,255,255], colorSpace='rgb255')
            text_decision.draw()
            
            win.flip()
            
            k = event.waitKeys(keyList=['c', 'm'])
            
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_END %d"%t,sec_time=flip_time)
            tracker.setRecordingState(False)

            self.hub.clearEvents('all')
            
            return k[0]
           
        
        ###########
        #### Susa's experiment functions
        ###########

                
        

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
        print(csv_name)
        cs=open(csv_name,'wb')
        
        #define the columns 
        fieldnames = ['trial','subject','partner','Role','item','Condition','A_self','A_other','B_self','B_other','Choice_A','Choice_accept']
        writer = csv.DictWriter(cs, fieldnames=fieldnames)
        writer.writeheader()
        
        
        #show waiting message
        message1.draw()
        win.flip()

        
        #variables
        inst1.image = 'Instructions\Inst.png'
        

        
        inst2.image='Instructions\Player_A.png'

        
        
        inst1.draw()
        win.flip()
        key=event.waitKeys(keyList=['space'])
        inst2.draw()
        win.flip()
        key=event.waitKeys(keyList=['space'])
        
       
        #show example message
        example_message = visual.TextStim(win, text="Probedurchgang (dieser wird nicht relevant für Ihre spätere Auszahlung)", pos = [0,0], height=30,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.7)
        example_message.draw()
        win.flip()
        #core.wait(5)

                            
        ''' ### Show an example of 3 trials ...
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
                
        '''
                #log file data
                fill_row(writer,subj_id,partner_ID,t,my_role,prop_data[item],key,partner_data,order)
          
            elif my_role=='responder':
                #wait till the partner send the propsel/////////////////triger 9
                message1_r.draw()
                win.flip()
                connection.data['example_choice'].append(' ') # send selection to the DB
                connection.push()
                
                while True:
                    if len(connection.get(partner)['data']['example_choice']) > t:
                        break
                
                
                #connection.wait(lambda doc: len(doc['data']['example_choice'])>(t),check='partner')
                
                partner_data=connection.get(partner)['data']['example_choice'][-1]
                
                #swap your gain with partner gain and partner gain with your gain
                temp_swap=partner_data[1]
                partner_data[1]=partner_data[2]
                partner_data[2]=temp_swap
                
                temp_swap=partner_data[5]
                partner_data[5]=partner_data[6]
                partner_data[6]=temp_swap
               
                
                #show Blank screen////////// triger 1
                win.flip()
                time.sleep(0.5)
                
                #send accept or reject to your partner///////////triger 5
                accept=accept_proposal(win,partner_data,order)
                connection.data['example_response'].append(accept) # send selection to the DB
                connection.push()
                
                '''
        '''
                #show message////////////triger 6
                if accept:
                    message2_r.text="Sie haben die Entscheidung des anderen Spielers akzeptiert."
                else:
                    message2_r.text="Sie haben die Entscheidung des anderen Spielers abgelehnt."
                message2_r.draw()
                win.flip()
                time.sleep(2)
                '''
        '''
                #log file data partner_data looks like [nu1,nu2,nu3,nu4,c/m]
                fill_row(writer,subj_id,partner_ID,t,my_role,partner_data[:-1],partner_data[-1:],accept,order)

        for t in range(0,n_example_trial):
            do_example_trial(win, c, t, writer,subj_id,partner_ID, my_role, example_prop_data, item_list, order, messages)
        
        cs.close()
        new_feedback(win,c,my_role,csv_name, True)
        key=event.waitKeys(keyList=['space'])
        
        #------------------------------------------------------------Trial Example ends ----------------------------------------------------------------------------------------------
        
        
        
        
        
        #------------------------------------------------------------Trial Logic starts ----------------------------------------------------------------------------------------------
        
        #get time in nice format to name the csv file
        localtime=time.asctime(time.localtime(time.time()))
        localtime=localtime[11:16]+'pm-'+localtime[4:10]
        localtime=localtime.replace(":","_").replace(" ","_")
        
        #create csv file
        csv_name='Exp Results\\'+subj_id+'_Experiment_info'+localtime+'.csv'
        cs=open(csv_name,'wb')
        
        #define the columns 
        fieldnames = ['trial','subject','partner','Role','item','Condition','A_self','A_other','B_self','B_other','Choice_A','Choice_accept']
        writer = csv.DictWriter(cs, fieldnames=fieldnames)
        writer.writeheader()
        
                            
        #show experiment_begins message
        start_message = visual.TextStim(win, text="Nun beginnen die auszahlungsrelevanten Aufgaben.", pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        start_message.draw()
        win.flip()
        core.wait(5)
        
        #receive the id of your partner
        partner=c.current_partners[0]


        c.wait(lambda doc: len(doc['data']['info'])>(0),check='partner')
        partner_ID=c.get(partner)['data']['info'][-1]
    
        flip_time=win.flip()
        self.hub.sendMessageEvent(text="EXPERIMENT_START",sec_time=flip_time)
        self.hub.clearEvents('all')
    
        prop_data=get_proposals_data('prop_data.csv')
        main_prop_data = prop_data[1:]
        item_list=range(0,len(main_prop_data))
        n_trial = len(main_prop_data)
        
        if my_role=='proposer':
            inst2.image='Instructions\Player_A.png'  
        else:
            inst2.image='Instructions\Player_B.png'


        # Send some information to the ioHub DataStore as experiment messages
        # including the eye tracker being used for this session.
        #
        self.hub.sendMessageEvent(text="IO_HUB EXPERIMENT_INFO START")
        self.hub.sendMessageEvent(text="ioHub Experiment started {0}".format(getCurrentDateTimeString()))
        self.hub.sendMessageEvent(text="Experiment ID: {0}, Session ID: {1}".format(self.hub.experimentID,self.hub.experimentSessionID))
        self.hub.sendMessageEvent(text="Stimulus Screen ID: {0}, Size (pixels): {1}, CoordType: {2}".format(display.getIndex(),display.getPixelResolution(),display.getCoordinateType()))
        self.hub.sendMessageEvent(text="Calculated Pixels Per Degree: {0} x, {1} y".format(*display.getPixelsPerDegree()))
        self.hub.sendMessageEvent(text="Eye Tracker being Used: {0}".format(selected_eyetracker_name))
        self.hub.sendMessageEvent(text="IO_HUB EXPERIMENT_INFO END")

        self.hub.clearEvents('all')        '''
    
        '''def do_trial(win, tracker, connection, t, fixation_cross, writer,subj_id,partner_ID, my_role, prop_data, item_list, order, messages):
            # So request to start trial has occurred...
            # Clear the screen, start recording eye data, and clear all events
            # received to far.
            
            message1 = messages[0]
            message1_p = messages[1]
            message2_p = messages[2]
            message1_r = messages[3]
            message2_r = messages[4]
             
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_START",sec_time=flip_time)
            self.hub.clearEvents('all')
            tracker.setRecordingState(True)
            
            if my_role=='proposer':
                #show Blank screen////////////triger 1
                win.flip()
                tracker.setTriggerValue(1000+t+1)
                time.sleep(0.5)
                
                #show fixation_cross///////////triger 2
                fixation_cross.draw()
                win.flip()
                tracker.setTriggerValue(2000+t+1)
                time.sleep(0.5)
                
                #select an item randomly from the CSV file with no replacment
                random.shuffle(item_list)
                item=item_list[0]
                del item_list[0]
                
                #select a proposal and send it to the partner//////////////triger 3
                tracker.setTriggerValue(3000+t+1)
                key=choose_proposal(win,prop_data[item],order)
                send=prop_data[item]+key
                connection.data['choice'].append(send) # send selection to the DB
                connection.push()
                
                #show message//////////////////triger 9
                message1_p.draw()
                win.flip()
                tracker.setTriggerValue(9000+t+1)
                
                #wait for the responder to reject/accept
                connection.data['response'].append(' ') # send selection to the DB
                connection.push()
                
                while True:
                    if len(connection.get(partner)['data']['response']) > t:
                        break
                
                #connection.wait(lambda doc: len(doc['data']['response'])>(t),check='partner')

                partner_data=connection.get(partner)['data']['response'][-1]
                
                #### Please comment in this section in case reponder/proposal asks for feedback 
                '''
        '''
                #show message//////////////////triger 4
                if partner_data:
                    message2_p.text="Ihre Entscheidung wurde akzeptiert."
                else:
                    message2_p.text="Ihre Entscheidung wurde abgelehnt."
                message2_p.draw()
                win.flip()
                tracker.setTriggerValue(4000+t+1)
                time.sleep(2)
                '''
        '''
                #log file data
                fill_row(writer,subj_id,partner_ID,t,my_role,prop_data[item],key,partner_data,order)
            elif my_role=='responder':
                #wait till the partner send the propsel/////////////////triger 9
                message1_r.draw()
                win.flip()
                tracker.setTriggerValue(9000+t+1)
                connection.data['choice'].append(' ') # send selection to the DB
                connection.push()
                
                while True:
                    if len(connection.get(partner)['data']['choice']) > t:
                        break
                
                #connection.wait(lambda doc: len(doc['data']['choice'])>(t),check='partner')
                
                partner_data=connection.get(partner)['data']['choice'][-1]
                
                #swap your gain with partner gain and partner gain with your gain
                temp_swap=partner_data[1]
                partner_data[1]=partner_data[2]
                partner_data[2]=temp_swap
                
                temp_swap=partner_data[5]
                partner_data[5]=partner_data[6]
                partner_data[6]=temp_swap
               
                
                #show Blank screen////////// triger 1
                win.flip()
                tracker.setTriggerValue(1000+t+1)
                time.sleep(0.5)
                
                #show fixation_cross///////////triger 2
                fixation_cross.draw()
                win.flip()
                tracker.setTriggerValue(2000+t+1)
                time.sleep(0.5)
                
                #send accept or reject to your partner///////////triger 5
                tracker.setTriggerValue(5000+t+1)
                accept=accept_proposal(win,partner_data,order)
                connection.data['response'].append(accept) # send selection to the DB
                connection.push()

                #### Please comment in this section in case reponder/proposal asks for feedback 
                '''
        '''
                #show message////////////triger 6
                if accept:
                    message2_r.text="Sie haben die Entscheidung des anderen Spielers akzeptiert."
                else:
                    message2_r.text="Sie haben die Entscheidung des anderen Spielers abgelehnt."
                message2_r.draw()
                win.flip()
                tracker.setTriggerValue(6000+t+1)
                time.sleep(2)
               '''
        '''
                #log file data partner_data looks like [nu1,nu2,nu3,nu4,c/m]
                fill_row(writer,subj_id,partner_ID,t,my_role,partner_data[:-1],partner_data[-1:],accept,order)



            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_END %d"%t,sec_time=flip_time)
            tracker.setRecordingState(False)

            self.hub.clearEvents('all')
            
        
        for t in range(0,n_trial):
            do_trial(win, tracker, c, t, fixation_cross, writer,subj_id,partner_ID, my_role, main_prop_data, item_list, order, messages)
        '''
        cs.close()
        
        event.waitKeys(keyList=['space'])
        #------------------------------------------------------------Trial Logic ends ----------------------------------------------------------------------------------------------
        #------------------------------------------------------------Susa experiment ends ----------------------------------------------------------------------------------------------
        
            
        #------------------------------------------------------------Fiona experiment begins ----------------------------------------------------------------------------------------------
        '''instructions_2(win)
    
        # get data...
        data = read_input_file_2(input_file_2_dir)
        entscheider = data[2]
        empfanger = data[3]
        eingreifen = data[8]
        
        dictator_payoff = data[5]
        intervened = data[0]
        
        bestrafung = data[4]
        kosten = data[7]
   
        if con < 13:
            decision = draw1_player_ab(win, tracker, 9901, '9.42', '3.99', '5.40', '1.34', '4.02')
        else:
            decision = draw2_player_ab(win, tracker, 9901, '9.42', '3.99', '5.40', '1.34', '4.02')
        
        start_message = visual.TextStim(win, text="Auf dem nächsten Bildschirm werden Sie die auszahlungsrelevante Entscheidung treffen.\n Bitte drücken Sie die Leertaste.", pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
        start_message.draw()
        win.flip()
        key=event.waitKeys(keyList=['space'])
        
        if con < 13:
            decision = draw1_player_ab(win, tracker, 9902, entscheider, empfanger, eingreifen, kosten, bestrafung)
        else:
            decision = draw2_player_ab(win, tracker, 9902, entscheider, empfanger, eingreifen, kosten, bestrafung)
        
        
        # write results to an outout file...
        to_output_2(subj_id, decision)

        draw_final_payoff(win, c, first_payoff, decision, dictator_payoff,  intervened)
        
        event.waitKeys(keyList=['f2']) '''
        
        t=10
        trigger_value=6000+t
        draw1_player_ab(win, tracker, trigger_value)

        #------------------------------------------------------------Fiona experiment ends ----------------------------------------------------------------------------------------------

        # Disconnect the eye tracking device.
        
        #
        tracker.setConnectionState(False)
        
        
        flip_time=win.flip()
        self.hub.sendMessageEvent(text="SHOW_DONE_TEXT",sec_time=flip_time)
        print('hiii')
        cs.close()
        print('hii2i')
           
        # So the experiment is done, all trials have been run.
        # Clear the screen and show an 'experiment  done' message using the
        # instructionScreen state. What for the trigger to exit that state.
        # (i.e. the space key was pressed)
        #
        self.hub.sendMessageEvent(text='EXPERIMENT_COMPLETE')
        
        print('hiii3')
        tex1=eventtxt.Eventtotext()
        print('hiii4')
        tex1.convertToText(exp_script_dir,subj_id,localtime)
        
        print('hiii5')
        
        
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

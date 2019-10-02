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


subject_id='-1'
con=1
calibration_failed = 0

input_file_dir = 'input.csv'
output_file_dir = 'Exp Results\\output.csv'
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
        def to_output(subject_id, decision, trigger_value, input_decision, output_file_dir):

            import os.path 

            is_exist = False
            if os.path.exists(output_file_dir): is_exist = True

            # Add header to the output file if it is the first time to write to it...
            if not is_exist:    
                output_data_headers = ['Subject_id', 'Decision', 'Trigger','Input of made choice']
                      

            # Python 2
            with open(output_file_dir, 'ab') as f:

            # Python 3
            #with open(output_file_dir, 'a', newline = '') as f:

                writer = csv.writer(f)
                if not is_exist:
                    writer.writerows([output_data_headers])
                
                writer.writerows([[subject_id, decision, trigger_value, input_decision]])
                
        def read_input_file(csv_dir, item_number):
    
            global subject_id
            i=0
            
            with open(csv_dir, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter='\n', quotechar='|')
                print(spamreader)
               
                for row in spamreader:
                    i=i+1
                    if (i==item_number):
                        print(subject_id, row, str(subject_id))
                        return row
                        
            return 0
        
        def logs_windows(log_text, log_key_to_proceed):

            start_message = visual.TextStim(win, text=log_text, pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
            start_message.draw()
            win.flip()
            key=event.waitKeys(keyList=[log_key_to_proceed])
            return key

        def instructions_blank_screen(win):

            inst_dir = 'Instructions\\blank_screen.jpg'
            #maybe blank screen is just grey screen, but not white
            instr=visual.ImageStim(win,image=inst_dir, units='pix', size = (1600, 900))
            instr.draw()
            win.flip()
            key=event.waitKeys(keyList=['space'])
        
        def instructions_fixation_cross(win):

            inst_dir = 'Instructions\\fixation_cross.jpg'
            #fixation_cross = visual.TextStim(win, text='+', pos = [0,0], height=54,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
            instr=visual.ImageStim(win,image=inst_dir, units='pix', size = (1600, 900))
            instr.draw()
            win.flip()
            key=event.waitKeys(keyList=['space']) 
            
        def instructions_choice_decision(win):

            inst_dir = 'Instructions\\choice_decision.jpg'
            instr=visual.ImageStim(win,image=inst_dir, units='pix', size = (1600, 900))
            #add table part here with input tables as random trials
            
            #make use of permutations - 'random'
            
            '''all possible permutations for order variable (instead of using if statment)
        permutations={1: '0123', 2: '0132',3: '0213', 4: '0231',5:'0312' , 6: '0321',
                      7: '1023', 8: '1032',9: '1203', 10: '1230',11: '1302',12: '1320',
                     13:'2013', 14: '2031',15:'2103',16:'2130',17:'2301',18:'2310',
                     19:'3012',20:'3021',21:'3102', 22:'3120',23:'3201', 24: '3210'}
                     
        order=permutations[con] '''
        
            instr.draw()
            win.flip()
            key=event.waitKeys(keyList=['c', 'm']) 
            return key
    
        def draw_trigger(win, tracker, trigger, item_number, output_file_dir):
            
            global input_file_dir
            
            choice = 0
    
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_START",sec_time=flip_time)
            self.hub.clearEvents('all')
            tracker.setRecordingState(True)
            
            tracker.setTriggerValue(trigger)
            input_decision = read_input_file(input_file_dir, item_number)
            
            if (trigger == 1001):
                instructions_blank_screen(win)
                to_output(subject_id, 'space (proceed)', trigger, input_decision, output_file_dir)
                
            
            if (trigger == 2001):
                instructions_fixation_cross(win)
                to_output(subject_id, 'space (proceed)', trigger, input_decision, output_file_dir)
                
            if (trigger == 3001):
                choice = instructions_choice_decision(win)
                to_output(subject_id, choice, trigger, input_decision, output_file_dir)
                
            
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_END %d"%t,sec_time=flip_time)
            tracker.setRecordingState(False)

            self.hub.clearEvents('all')
            
            return choice
           
        
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
        # would need it for later
        mouse.setSystemCursorVisibility(False)
        event.Mouse(visible=False)

        
        #------------------------------------------------------------Experiment begins ----------------------------------------------------------------------------------------------
        
        #get time in nice format to name the csv file
        localtime=time.asctime(time.localtime(time.time()))
        localtime=localtime[11:16]+'pm-'+localtime[4:10]
        localtime=localtime.replace(":","_").replace(" ","_")
        
        #create csv file
        csv_name='Exp Results\\'+subject_id+'_Example_info'+localtime+'.csv'
        csv_experiment_output ='Exp Results\\'+subject_id+'_output'+localtime+'.csv'
        
        print(csv_name)
        cs=open(csv_name,'wb')
        print(cs)
        
        #define the columns 
        fieldnames = ['Subject_id', 'Decision', 'Trigger','Input of made choice']
        writer = csv.DictWriter(cs, fieldnames=fieldnames)
        writer.writeheader()
        
        #variables
        inst1=visual.ImageStim(win,pos=(0,0))
        
        #draw instruction
        inst1.image = 'Instructions\Inst.png'
        inst1.draw()
        win.flip()
        key=event.waitKeys(keyList=['space'])
        
        #show example message
        #example_message = visual.TextStim(win, text="Probedurchgang (dieser wird nicht relevant für Ihre spätere Auszahlung)", pos = [0,0], height=30,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.7)
        #example_message.draw()
        
        #'''cs.close()'''
        
        
                            
        #show logs window message with '1', proceed with space
        logs_windows('1', 'space')

        flip_time=win.flip()
        self.hub.sendMessageEvent(text="EXPERIMENT_START",sec_time=flip_time)
        self.hub.clearEvents('all')
    
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
        
        #show logs window message with '2', proceed with space
        logs_windows('2', 'space')

        self.hub.clearEvents('all')         # why here clear events
        
        #show logs window message with '3', proceed with space
        logs_windows('3', 'space')
        
        
        for t in range(2):
            #show logs window message with '4', proceed with space
            logs_windows('4', 'space')
            
            trigger_value=1001
            draw_trigger(win, tracker, trigger_value, t+2,csv_experiment_output) #the row indexing starts from 2
            
            #show logs window message with '5', proceed with space
            logs_windows('5', 'space')
            
            trigger_value=2001
            draw_trigger(win, tracker, trigger_value, t+2, csv_experiment_output)
            
            #show logs window message with '6', proceed with space
            logs_windows('6', 'space')
            
            trigger_value=3001
            draw_trigger(win, tracker, trigger_value, t+2, csv_experiment_output)
            
            #show logs window message with '7', proceed with space
            logs_windows('7', 'space')

        #show logs window message with '8', proceed with space
        logs_windows('8', 'space')
        print('after 8')

        #------------------------------------------------------------Experiment ends ----------------------------------------------------------------------------------------------

        # Disconnect the eye tracking device.
        
        tracker.setConnectionState(False)
        
        
        flip_time=win.flip()
        self.hub.sendMessageEvent(text="SHOW_DONE_TEXT",sec_time=flip_time)
        print('hiii')
        #cs.close() #another one close
        print('hii2i')
        
        self.hub.clearEvents('all')
           
        # So the experiment is done, all trials have been run.
        # Clear the screen and show an 'experiment  done' message using the
        # instructionScreen state. What for the trigger to exit that state.
        # (i.e. the space key was pressed)
        #
        
        #'experiment  done', redo using instructionScreen state
        logs_windows("The experiment is complete. Press 'f2' to exit", 'f2')
        
        self.hub.sendMessageEvent(text='EXPERIMENT_COMPLETE')
        
        print('hiii3')
        tex1=eventtxt.Eventtotext()
        print('hiii4')
        tex1.convertToText(exp_script_dir,subject_id,localtime)
        
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
        global subject_id
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
            subject_id=str(info['Subject_ID'])
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

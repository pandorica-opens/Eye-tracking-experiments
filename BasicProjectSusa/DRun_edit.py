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
from psychopy import visual, event, core, logging
from psychopy.preferences import prefs
from psychopy.core import getTime, wait 
from psychopy.data import importConditions, TrialHandler
from psychopy.iohub import (EventConstants, EyeTrackerConstants,
                            getCurrentDateTimeString, ioHubExperimentRuntime)
import os
import random
import site
site.addsitedir('C:\Users\Standard\Miniconda2\Lib\site-packages')
from psynteract import Connection 
import psynteract
import socket
import csv
import eventtxt
import subprocess
import time
import math
import numpy as np


subject_id='-1'
con=1
calibration_failed = 0

input_file_dir = 'input.csv'
#output_file_dir = 'Exp Results\\output.csv'
logfile = logging.LogFile(f= 'Error Results.txt', level = 30, filemode = 'a', logger = None, encoding = 'utf8') #not working

#create global shutdown key
prefs.general['shutdownKey'] = 'q'


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
                                                       
        #TrialHandler(trialList, nReps, method=’random’, dataTypes=None, extraInfo=None, seed=None, originPath=None, name=’‘, autoLog=True)
        trials = TrialHandler(exp_conditions, 1) # 1 - number of repetitions, how do we use conditions lets try to comment out
        # Inform the ioDataStore that the experiment is using a
        # TrialHandler. The ioDataStore will create a table
        # which can be used to record the actual trial variable values (DV or IV)
        # in the order run / collected.
        #
        self.hub.createTrialHandlerRecordTable(trials)
        
        #Use Esc to quit, it will be called at some stages during the experiment
        def _checkQuit(key):
            if key[0]=='escape':
                os._exit(1)
                core.quit()
        
        ###########
        #### Experiment functions
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
                
        def to_output_eyetracking(subject_id, x, y, gazetime, trigger, output_eye_file_dir):

            import os.path 

            is_exist = False
            if os.path.exists(output_eye_file_dir): is_exist = True

            # Add header to the output file if it is the first time to write to it...
            if not is_exist:    
                output_data_headers = ['Subject_id', 'x', 'y', 'gazetime', 'Trigger']
                      

            # Python 2
            with open(output_eye_file_dir, 'ab') as f:

            # Python 3
            #with open(output_file_dir, 'a', newline = '') as f:

                writer = csv.writer(f)
                if not is_exist:
                    writer.writerows([output_data_headers])
                
                writer.writerows([[subject_id, x, y, gazetime, trigger]])
                
        def row_to_condition(row):
            txt=row
            #array_column_names 
            #print(txt.split(';'))
            a = np.empty(len(txt.split(';')))
            a = txt.split(';')
            #print('a', a)
            return a
                
        def read_input_file(csv_dir, item_number):
    
            global subject_id
            i=0
            
            with open(csv_dir, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter='\n', quotechar='|')
                #print(spamreader)
               
                for row in spamreader:
                    i=i+1
                    if (i==item_number):
                        #print('row', row)
                        return row
                        
            return 0
            
        def monitor_coordinate_check(win):
            for i in range(90):
                
                
                texti = str(-450+10*i) #-display_resolution[1]/2
                
                pixel_line_y = visual.ShapeStim(win, units='pix', lineWidth=1.5,lineColor=(55,255,255),lineColorSpace='rgb255', vertices=((-750, -450+10*i),(750, -450+10*i)),closeShape=False, pos=(0, 0), size=1.2)
                pixel_name_y = visual.TextStim(win, text='y='+texti, height=10, units='pix', pos = [0,-450+10*i],color=[255,55,255],colorSpace='rgb255')
                
                texti = str(-800+i*20) #-display_resolution[0]/2
                
                pixel_line_x = visual.ShapeStim(win, units='pix', lineWidth=1.5,lineColor=(155,255,55),lineColorSpace='rgb255', vertices=((-800+i*20, -450),(-800+i*20, 450)),closeShape=False, pos=(0, 0), size=1) #what size param
                pixel_name_x = visual.TextStim(win, text=texti, height=9, units='pix', pos = [-800+i*20,0],color=[255,55,55],colorSpace='rgb255')
                
                pixel_line_x.draw()
                pixel_line_y.draw()
                pixel_name_x.draw()
                pixel_name_y.draw()
            
           
            win.flip()
            
        def draw_input(win, item_array_text, item_array_x, item_array_y):
            
            for i in range(len(item_array_x)):
                #print(item_array_x[i], item_array_y[i], i, len(item_array_x), len(item_array_text), item_array_text)
                whitebox = visual.ShapeStim(win, units='pix', lineWidth=1.5,
                                            lineColor=(255,255,255),lineColorSpace='rgb255', 
                                            vertices=((item_array_x[i]+20, item_array_y[i]+20),
                                            (item_array_x[i]+20, item_array_y[i]-20),
                                            (item_array_x[i]-20, item_array_y[i]-20),
                                            (item_array_x[i]-20, item_array_y[i]+20)),
                                            closeShape=True, 
                                            fillColor = (255,255,255), fillColorSpace='rgb255',
                                            pos=(0, 0), size=1) #what size param
                whitebox.draw()
                
                item_value = visual.TextStim(win, text=item_array_text[i+1], height=21, units='pix', #here we use i+1 because the first number is numbers item
                pos = [item_array_x[i],item_array_y[i]],color=[0,0,0],colorSpace='rgb255')
                
                item_value.draw()
                
            win.flip(clearBuffer=False)
            
        
        def logs_windows(log_text, log_key_to_proceed):

            start_message = visual.TextStim(win, text=log_text, pos = [0,0], height=35,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.9)
            start_message.draw()
            win.flip()
            core.wait(0.2)
            key=event.waitKeys(keyList=[log_key_to_proceed])
            return key

        def instructions_blank_screen(win):

            inst_dir = 'Instructions\\blank_screen.jpg'
            instr=visual.ImageStim(win,image=inst_dir, units='pix', size = (1600, 900))
            
            draw_gaze_dot(win, 1001, 1) #change 1 second to 0.5 seconds
            #print(event.id)
            #print(tracker.getPosition()) #tracker - get position = none
            #print(kb.getEvents())  #kb.getEvents(event_type_id)
            
            for events in tracker.getEvents():
                print(events, '\n')
                print('\n')
            
            '''KeyboardReleaseEventNT(experiment_id=1, session_id=1, device_id=0, 
                event_id=175, type=23, device_time=15105.28, logged_time=23.941098399425755, time=23.941098399425755, 
                confidence_interval=0.0, delay=0.0, filter_id=0, auto_repeated=0, scan_code=57, key_id=32, ucode=0, key=' ', 
                modifiers=[], window_id=1049896, char=u' ', duration=0.059997031472448725, press_event_id=172), 
                
                KeyboardPressEventNT(experiment_id=1, session_id=1, device_id=0, event_id=179, type=22, device_time=15105.374, 
                logged_time=24.041724395678102, time=24.041724395678102, confidence_interval=0.0, delay=0.0, filter_id=0, 
                auto_repeated=0, scan_code=57, key_id=32, ucode=0, key=' ', modifiers=[], window_id=1049896, char=u' ', duration=0.0, 
                press_event_id=0), 
                
                KeyboardReleaseEventNT(experiment_id=1, session_id=1, device_id=0, event_id=181, type=23, 
                device_time=15105.436, logged_time=24.101254831381084, time=24.101254831381084, confidence_interval=0.0, delay=0.0, 
                filter_id=0, auto_repeated=0, scan_code=57, key_id=32, ucode=0, key=' ', modifiers=[], window_id=1049896, char=u' ', 
                duration=0.05953043570298178, press_event_id=179), 
                
                KeyboardPressEventNT(experiment_id=1, session_id=1, device_id=0, 
                event_id=185, type=22, device_time=15105.53, logged_time=24.201119747564007, time=24.201119747564007, confidence_interval=0.0, 
                delay=0.0, filter_id=0, auto_repeated=0, scan_code=57, key_id=32, ucode=0, key=' ', modifiers=[], window_id=1049896, char=u' ', 
                duration=0.0, press_event_id=0), 
                
                KeyboardReleaseEventNT(experiment_id=1, session_id=1, device_id=0, event_id=188, type=23, 
                device_time=15105.592, logged_time=24.26133744488652, time=24.26133744488652, confidence_interval=0.0, delay=0.0, filter_id=0, 
                auto_repeated=0, scan_code=57, key_id=32, ucode=0, key=' ', modifiers=[], window_id=1049896, char=u' ', duration=0.06021769732251414, 
                press_event_id=185), 
                
                KeyboardPressEventNT(experiment_id=1, session_id=1, device_id=0, event_id=195, type=22, device_time=15105.764, 
                logged_time=24.44114932231423, time=24.44114932231423, confidence_interval=0.0, delay=0.0, filter_id=0, auto_repeated=0, scan_code=57, 
                key_id=32, ucode=0, key=' ', modifiers=[], window_id=1049896, char=u' ', duration=0.0, press_event_id=0)]'''
            
            
            #print(display.getEvents()) #empty list
            #here we want FixationStartEvent or FixationEndEvent
            
            '''[BinocularEyeSampleEventNT(experiment_id=1, 
                session_id=1, device_id=0, event_id=87, type=52, device_time=211052.468, logged_time=20.073157634193194, time=211052.4679924997, 
                confidence_interval=0.0, delay=-211032.39483486552, filter_id=1001, left_gaze_x=0, left_gaze_y=0, left_gaze_z=0, left_eye_cam_x=0,
                left_eye_cam_y=0,
                left_eye_cam_z=0, left_angle_x=0, left_angle_y=0, left_raw_x=0, left_raw_y=0, left_pupil_measure1=0, left_pupil_measure1_type=70, 
                left_pupil_measure2=0, left_pupil_measure2_type=0, left_ppd_x=0, left_ppd_y=0, left_velocity_x=0, left_velocity_y=0, left_velocity_xy=0, 
                right_gaze_x=0, right_gaze_y=0, right_gaze_z=0, right_eye_cam_x=0, right_eye_cam_y=0, right_eye_cam_z=0, right_angle_x=0, right_angle_y=0, 
                right_raw_x=0, right_raw_y=0, right_pupil_measure1=0, right_pupil_measure1_type=70, right_pupil_measure2=0, right_pupil_measure2_type=0, 
                right_ppd_x=0, right_ppd_y=0, right_velocity_x=0, right_velocity_y=0, right_velocity_xy=0, status=16), 
                
                BinocularEyeSampleEventNT(experiment_id=1, session_id=1, device_id=0, event_id=106, type=52, device_time=211053.06, 
                logged_time=20.633184666747184, time=211053.05999328924, confidence_interval=0.0, delay=-211032.4268086225, filter_id=1001,
                left_gaze_x=0, left_gaze_y=0, left_gaze_z=0, left_eye_cam_x=0, left_eye_cam_y=0, left_eye_cam_z=0, left_angle_x=0, 
                left_angle_y=0, left_raw_x=0, left_raw_y=0, left_pupil_measure1=0, left_pupil_measure1_type=70, left_pupil_measure2=0, 
                left_pupil_measure2_type=0, left_ppd_x=0, left_ppd_y=0, left_velocity_x=0, left_velocity_y=0, left_velocity_xy=0, 
                right_gaze_x=0, right_gaze_y=0, right_gaze_z=0, right_eye_cam_x=0, right_eye_cam_y=0, right_eye_cam_z=0, right_angle_x=0,
                right_angle_y=0, right_raw_x=0, right_raw_y=0, right_pupil_measure1=0, right_pupil_measure1_type=70, right_pupil_measure2=0,
                right_pupil_measure2_type=0, right_ppd_x=0, right_ppd_y=0, right_velocity_x=0, right_velocity_y=0, right_velocity_xy=0, status=16)]'''
            
            
            #print(mouse.getEvents()) #empty list
        
        def instructions_fixation_cross(win):

            #inst_dir = 'Instructions\\fixation_cross.jpg'
            #instr=visual.ImageStim(win,image=inst_dir, units='pix', size = display_resolution)
            #instr.draw()
            
            fixation_cross = visual.TextStim(win, text='+', pos = [-595,345], height=54,color=[-1,-1,-1],colorSpace='rgb')
            fixation_cross.autoDraw = True
            draw_gaze_dot(win, 2001, 1) #change 1 second to 0.5 seconds
            #monitor_coordinate_check(win)
            #win.flip() #comment in case of monitor coordinate check
            fixation_cross.autoDraw = False
            
        def instructions_choice_decision(win, item_list_text):
            
            inst_dir = 'Instructions\\choice_decision.jpg'
            instr=visual.ImageStim(win,image=inst_dir, units='pix', size = display_resolution)
            instr.draw()
            
            #item_list_text = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
            item_array_x = np.array([-15, -15, -15, -15,-15, -15, 445, 445, 445, 445, 445, 445])
            item_array_y = np.array([215,105,-5,-115,-225,-335,215,105,-5,-115,-225,-335])
            
            draw_input(win, item_list_text, item_array_x, item_array_y)
            #monitor_coordinate_check(win)
            draw_gaze_dot(win, 3001, 1000)
            
            #key=event.waitKeys(keyList=['c', 'm']) 
            return key
    
        def draw_trigger(win, tracker, trigger, item_number, output_file_dir, output_eye_dir):
            
            global input_file_dir
            
            choice = 0
    
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_START",sec_time=flip_time)
            self.hub.clearEvents('all')
            tracker.setRecordingState(True) #setting it every time here - why
            
            tracker.setTriggerValue(trigger)
            input_to_make_decision = read_input_file(input_file_dir, item_number)
            #print(input_to_make_decision, type(input_to_make_decision), ''.join(input_to_make_decision))
            
            input_to_make_decision_split = ''.join(input_to_make_decision)
            input_to_make_decision_split = row_to_condition(input_to_make_decision_split)
            #print(input_to_make_decision_split)
            
            #change x,y, gazetime while testing with eyetribe
            x,y,gazetime = 10, 20, 30

            
            if (trigger == 1001):
                instructions_blank_screen(win)
                to_output(subject_id, 'space', trigger, input_to_make_decision, output_file_dir)
                to_output_eyetracking(subject_id, x, y, gazetime, trigger, output_eye_dir)
                
            
            if (trigger == 2001):
                instructions_fixation_cross(win)
                to_output(subject_id, 'space', trigger, input_to_make_decision, output_file_dir)
                to_output_eyetracking(subject_id, x, y, gazetime, trigger, output_eye_dir)
                
            if (trigger == 3001):
                choice = instructions_choice_decision(win, input_to_make_decision_split)
                to_output(subject_id, choice, trigger, input_to_make_decision, output_file_dir)
                to_output_eyetracking(subject_id, x, y, gazetime, trigger, output_eye_dir)
                
            
            flip_time=win.flip()
            self.hub.sendMessageEvent(text="TRIAL_END %d"%t,sec_time=flip_time)
            tracker.setRecordingState(False)

            self.hub.clearEvents('all')
            
            return choice
            
        def draw_gaze_dot(win, trigger, time):
            #try to paint gaze position
            
            stime = getTime()
        
            while getTime()-stime < time:
                gpos = tracker.getPosition()
                #print('binocular', tracker.FixationEndEvent())
                #obj = tracker.BinocularEyeSampleEvent(EyeTrackerEvent)
                #print(obj)
                #print('binocular left gaze x', tracker.BinocularEyeSampleEvent.left_gaze_x())
                #left_gaze_x
                if (gpos != None):
                    #print('gpos, tracker.getPosition()', gpos, tracker.getPosition()) basically gpos and tracker.getPosition are the same, so it gets executed in the matter of milliseconds
                    #start_message = visual.TextStim(win, text=str(gpos)+str(trigger), pos = [gpos[0],gpos[1]], height=10,color=[-1,-1,-1],colorSpace='rgb',wrapWidth=win.size[0])
                    start_message = visual.TextStim(win, text='+', pos = [gpos[0],gpos[1]], height=10,color=[-1,-1,-1],colorSpace='rgb',wrapWidth=win.size[0])
                    start_message.draw()
                    
                    #start_message = visual.TextStim(win, text=str(gpos), pos = [gpos[1],gpos[0]], height=35,color=[-1,-1,-1],colorSpace='rgb',wrapWidth=win.size[0]*.9)
                    #start_message.draw()
                    win.flip(clearBuffer=False)
                    core.wait(0.005)
                    
                key = event.getKeys(keyList=['c', 'm'])
                #print('key event draw gaze dot', key)
                if key!=[]:
                    break
                
            return 0
        

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
        waitBlanking=False, color="white")
        
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
        csv_eye_output='Exp Results\\'+subject_id+'_eyetracking_output'+localtime+'.csv'
        csv_experiment_output ='Exp Results\\'+subject_id+'_decision_output'+localtime+'.csv'
        
        
        tracker.setRecordingState(True)
        
        #draw instruction (1)
        
        #inst1.image = 'Instructions\Inst.png'
        inst1 = visual.TextStim(win, text='Instruction', pos = [0,0],
                                    height=24, color=[-1,-1,-1], colorSpace='rgb',
                                    alignHoriz='center', alignVert='center',
                                    wrapWidth=win.size[0]*.9)
        inst1.draw()
        
        flip_time=win.flip()
        self.hub.sendMessageEvent(text="EXPERIMENT_START",sec_time=flip_time)
        self.hub.clearEvents('all')
        
        key=event.waitKeys(keyList=['space'])
        
                            
        #show logs window message with '1', proceed with space
        #logs_windows('1', 'space')
        
         #------------------------------------------------------------Experiment trial testing ----------------------------------------------------------------------------------------------
        
        
    
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
        
        print('get current date time', "{0}".format(getCurrentDateTimeString()))
        print('experiment ID', self.hub.experimentID,'experiment session ID', self.hub.experimentSessionID) 
        print('display', "{0}".format(display.getIndex()), 'pixel resolution', "{0}".format(display.getPixelResolution()), 'coordinate type', "{0}".format(display.getCoordinateType()))
        print('pixels degree', "{0}".format(display.getPixelsPerDegree()), 'selected eyetracker', selected_eyetracker_name)

        #show logs window message with '2', proceed with space
        #logs_windows('2', 'space')

        self.hub.clearEvents('all')         # why here clear events
        
        #show logs window message with '3', proceed with space
        #logs_windows('3', 'space')

        #trials.printAsText() #does not work
        #tracker.getLastGazePosition()

        
        for t in range(2): #number of trials is 10
            self.hub.sendMessageEvent(text="TRIAL_START")
            self.hub.clearEvents('all')
            
            item_number = random.randrange(2, 11, 1)
            #print(item_number)
            
            #show logs window message with '4', proceed with space
            #logs_windows('4', 'space')
            
            trigger_value=1001
            draw_trigger(win, tracker, trigger_value, item_number,csv_experiment_output, csv_eye_output) #the row indexing starts from 2
            #draw_gaze_dot(win, trigger_value)
            
            #show logs window message with '5', proceed with space
            #logs_windows('5', 'space')
            
            trigger_value=2001
            draw_trigger(win, tracker, trigger_value, item_number, csv_experiment_output, csv_eye_output)
            
            #show logs window message with '6', proceed with space
            #logs_windows('6', 'space')
            
            trigger_value=3001
            draw_trigger(win, tracker, trigger_value, item_number, csv_experiment_output, csv_eye_output)

            flip_time=win.flip()
            self.hub.sendMessageEvent(text='TRIAL_END',sec_time=flip_time)
            self.hub.clearEvents('all')
        

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
        
        logs_windows("The experiment is complete. Press 'f2' to exit", 'f2')
        self.hub.sendMessageEvent(text="SHOW_DONE_TEXT")

        tex1=eventtxt.Eventtotext()
        tex1.convertToText(exp_script_dir,subject_id,localtime)
        self.hub.clearEvents('all')

        #self.hub.clearEvents('all', exp_script_dir) 
        
        # MANAGER ERROR WHEN SENDING MSG:[Errno 9] Bad file descriptor
        #Warning: TimeoutExpired, Killing ioHub Server process.
        
        #ioHubExperimentRuntime.shutdown()
        #print(ioHubExperimentRuntime)
        win.close()
        #io.quit()
        #print('end of exp logic')
        
        
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
        print('after runtime')
        runtime.start((dlg_info.values()[0],))
        print('after runtime info ')
        os.remove(configurationDirectory+"\events.hdf5")#this line to remove the hdf5 so in the next run of the expermint will not append
        print('after remove')
        
        if dlg_info.values()[0] =='The Eye Tribe':
            s.terminate()
            p.terminate()
        print('after terminate s,p')

    # Get the current directory, using a method that does not rely on __FILE__
    # or the accuracy of the value of __FILE__.
    #
    configurationDirectory=module_directory(main)

    # Run the main function, which starts the experiment runtime
    #
    main(configurationDirectory)

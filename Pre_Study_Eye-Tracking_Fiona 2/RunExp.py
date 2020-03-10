#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

# Import key parts of the PsychoPy library:
from psychopy import visual, event, core
from psychopy import gui

import os
import eventtxt
import subprocess
import csv
import time
import random

welcome_screen = 'welcome screen.PNG'

input_file_dir = 'Input_file.csv'
order_file_dir = 'order_input_file.csv'
output_file_dir = 'output_file.csv'
n_conditions = 8

points_in_euros = 0.014
showup_fee = 8.0



blank_screen_duration = 0.5 #in seconds...

code_table = {'0':'D', '1':'K', '2':'L', '3':'B', '4':'F', '5':'A', '6':'N', '7':'Q', '8':'X', '9':'E'}

def get_subject_info():
    #****************Collect Information about the Subject****************************
    order_list=range(1,25)
    info = {'Subject_ID':000,'Condition':[]}
    for i in xrange(1, n_conditions+1):
        info['Condition'].append('1'+str(i))

        
    infoDlg = gui.DlgFromDict(dictionary=info, title='Das Experiment',order=['Subject_ID','Condition'])
    if infoDlg.OK: #this will be True (user hit OK) or False (cancelled)
        subj_id=str(info['Subject_ID'])
        condition=str(info['Condition'])

        return subj_id,condition

    else:
        core.quit()

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
    to_output(subj_id, condition, exp_time, experiment_results)
    k = event.waitKeys(keyList=['f2', 'up', 'down'])
    if k[0] == 'f2':
        win.close()
        core.quit()
    elif k[0] == 'up' or 'down':
        pass

def to_output(output_file_dir, subj_id, condition, localtime, results):
    
    
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
            
            row = results[i]['pressup']
            row.append(results[i]['pressup_time'])
            row.append(results[i]['correct_answer'])
            
            row.insert(0,str(i+1)) 
            row.insert(1, str(subj_id))
            row.insert(2, str(condition))
            row.insert(3, str(localtime))
            row.insert(4, results[i]['picked_item'])
            
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
        Probedurchgang = visual.TextStim(win, text='Probedurchgang', pos = [0,450], units='pix', height=20,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.5)
        Probedurchgang.draw() 
    
    line = visual.Line(win, start=(-700, 0), end=(700, 0)) 
    
    # draw the tables
    tableA = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((-500, -100), (0, -100),(0, -430),(-500, -430), (-500, -100)),closeShape=False, pos=(-70, 0), size=1)
    tableB = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((0, -100), (500, -100),(500, -430),(0, -430), (0, -100)),closeShape=False, pos=(70, 0), size=1)
    
    label_1 = visual.TextStim(win, text=titles[int(display_order[0])-1], height=20, units='pix', pos = [-410,-200])
    label_2 = visual.TextStim(win, text=titles[int(display_order[1])-1], height=20, units='pix', pos = [-410,-330])
    label_3 = visual.TextStim(win, text=titles[int(display_order[2])-1], height=20, units='pix', pos = [410,-200])
    label_4 = visual.TextStim(win, text=titles[int(display_order[3])-1], height=20, units='pix', pos = [410,-330])
    
    number_1 = visual.TextStim(win, text=round_data[int(display_order[0])], height=20, units='pix', pos = [-210,-200])
    number_2 = visual.TextStim(win, text=round_data[int(display_order[1])], height=20, units='pix', pos = [-210,-330])
    number_3 = visual.TextStim(win, text=round_data[int(display_order[2])], height=20, units='pix', pos = [210,-200])
    number_4 = visual.TextStim(win, text=round_data[int(display_order[3])], height=20, units='pix', pos = [210,-330])
    
    
        
    line.draw()
    tableA.draw()
    tableB.draw()
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
    
    results = {'correct_answer':[], 'picked_item':round_data[0], 'points':0., 'pressup':'0', 'pressup_time':'99'}
    clock = core.Clock()
    draw_screen(win, round_data, pressup, is_trial)
    e=event.getKeys(keyList=['up', 'down','f2'])
    if len(e)>0:
        if e[0] in ['up'] and not pressup:
            pressup = 1
            results['pressup'] = '1'
            results['pressup_time'] = round(clock.getTime(), 2)
            
        elif e[0] in ['down'] and not pressup:
            pressup = 0
            results['pressup'] = '0'
            results['pressup_time'] = round(clock.getTime(), 2)

        if e[0] == 'up' and round_data[9] == '1':
            correct_answer = 1
            results['correct_answer'] = '1'
        
        elif e[0] == 'down' and round_data[9] == '0':
            correct_answer = 1
            results['correct_answer'] = '1'
            
        draw_screen(win, round_data, pressup, is_trial)
        
    k = event.waitKeys(keyList=['f2', 'up', 'down'])
    if k[0] == 'f2':
        win.close()
        core.quit()
    elif k[0] == ['up','down']:
        pass
    return results

def draw_payoff(win, selected_round_data, selected_round_results, trial_id=None):
    global display_order
    correct_answer_points = int(selected_round_data[4])
        
    if not trial_id:
        Probedurchgang = visual.TextStim(win, text='Probedurchgang', pos = [0,450], units='pix', height=20,color=[255,255,255],colorSpace='rgb255',wrapWidth=win.size[0]*.5)
        Probedurchgang.draw() 
        payoff_text_1 = "Würde dieser Durchgang zufällig gezogen werden, so würde folgendes gelten.\n\n "

    else:
        payoff_text_1 = "Danke für Ihre Teilnahme!\nRunde "+ str(trial_id) +" wurde zufällig ausgewählt und wird damit auszahlungsrelevant. Unten sehen Sie, wie diese Runde aussah.\n\n"

        
    if selected_round_results['correct_answer'] == '0':
        payoff_text_1 += "Sie haben in dieser Runde falsch entschieden.\n Sie erhalten daher kein Geld für diese Runde.\n"
    else:
        payoff_text_1 += "Sie haben in dieser Runde richtig entschieden. Sie erhalten daher "
        payoff_text_1 += str(correct_answer_points)
        payoff_text_1 += " Punkte, was umgerechnet "
        payoff_text_1 += ("%.2f" % round(correct_answer_points * points_in_euros,2)).replace('.',',')
        payoff_text_1 += " € sind."
        
    payoff_text_1_obj = visual.TextStim(win, text=payoff_text_1, height=25, units='pix', pos = [-520,250], wrapWidth=win.size[0]*.7, alignHoriz='left')
    payoff_text_1_obj.draw()

    if trial_id:
        payoff_text_2 = "Das Experiment ist hiermit beendet, bitte verlassen Sie ruhig den Raum.\n"
        payoff_text_2_obj = visual.TextStim(win, text=payoff_text_2, height=25, units='pix', pos = [-520,100], wrapWidth=win.size[0]*.9, alignHoriz='left')
        payoff_text_2_obj.draw()
        
    if not trial_id:
        continue_text = "Bitte drücken Sie die Pfeiltaste nach rechts (-->)"
        continue_text_obj = visual.TextStim(win, text=continue_text, height=25, units='pix', pos = [0,-480], wrapWidth=win.size[0]*.7, alignHoriz='center')
        continue_text_obj.draw()
        
    # draw the tables
    titles = ['Punkte A','Punkte B','Grenzpunkte','Auszahlung']
    # draw the tables
    tableA = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((-400, -100), (-5, -100),(-5, -430),(-400, -430), (-400, -100)),closeShape=False, pos=(-150, 0), size=1)
    tableB = visual.ShapeStim(win, units='pix', lineWidth=3.5,lineColor=(255,255,255),lineColorSpace='rgb255', vertices=((5, -100), (400, -100),(400, -430),(5, -430), (5, -100)),closeShape=False, pos=(150, 0), size=1)
    
    label_1 = visual.TextStim(win, text=titles[int(display_order[0])-1], height=20, units='pix', pos = [-390,-200])
    label_2 = visual.TextStim(win, text=titles[int(display_order[1])-1], height=20, units='pix', pos = [-390,-330])
    label_3 = visual.TextStim(win, text=titles[int(display_order[2])-1], height=20, units='pix', pos = [310,-200])
    label_4 = visual.TextStim(win, text=titles[int(display_order[3])-1], height=20, units='pix', pos = [310,-330])
    
    number_1 = visual.TextStim(win, text=selected_round_data[int(display_order[0])], height=20, units='pix', pos = [-270,-200])
    number_2 = visual.TextStim(win, text=selected_round_data[int(display_order[1])], height=20, units='pix', pos = [-270,-330])
    number_3 = visual.TextStim(win, text=selected_round_data[int(display_order[2])], height=20, units='pix', pos = [430,-200])
    number_4 = visual.TextStim(win, text=selected_round_data[int(display_order[3])], height=20, units='pix', pos = [430,-330])
    
    line = visual.Line(win, start=(-700, 0), end=(700, 0)) 


    
    tableA.draw()
    tableB.draw()
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
    
    text = "Vielen Dank für Ihre Teilnahme am Experiment. Das Experiment ist hiermit beendet. Bitte notieren Sie sich den unten angegebenen Code auf dem dafür vorgesehenen Blatt Papier. Nehmen Sie sowohl dieses Blatt, als auch Ihre Sitznummer mit und bewegen Sie sich langsam nach draußen. Dort werden Sie vom Experimentator die Auszahlung erhalten."
    text_obj = visual.TextStim(win, text=text, height=20, pos = [0, 200], units='pix', wrapWidth=win.size[0]*.7, alignHoriz='center')
    text_obj.draw()
    
    code = ''
    for l in range(0, len(str(payoff))):
        if payoff[l] in code_table:
            code += code_table[payoff[l]]
            
    code_text = visual.TextStim(win, text="Code: " + code, height=40, units='pix', pos = [0,0],color=[255,255,255],colorSpace='rgb255', wrapWidth=win.size[0]*.7)
    code_text.draw()
        
    win.flip()
    
    
    
        
####### Main  #######
if __name__ == "__main__":
   
    #****************Collect Information about the Subject****************************
    subj_id, condition = get_subject_info()
    exp_dir = os.getcwd()
            
    exp_time=get_time()

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
    for round_data in main_data:
        t += 1
        flip_time=win.flip()
        
        time.sleep(0.5)
        
        round_results = do_round(win, round_data, is_trial = False)
        
        experiment_results.append(round_results)
        win.flip()
        
        flip_time=win.flip()
                 
    #------------------------------------------------------------ Main Experiment Ends ----------------------------------------------------------------------------------------------
                   
    #================= Draw Last Screen (Payoff) ==================
    selected_round_idx = random.randint(0, len(experiment_results)-1)
    selected_round_results = experiment_results[selected_round_idx]
                    
    selected_round_data = []
    for round_data in main_data:
        if int(round_data[0]) == int(selected_round_results['picked_item']):
            selected_round_data = round_data
                            
    draw_payoff(win, selected_round_data, selected_round_results, trial_id=selected_round_idx+1)
    
    event.waitKeys(keyList=['f2'])
    
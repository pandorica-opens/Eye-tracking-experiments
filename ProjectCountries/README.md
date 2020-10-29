# The Experiment for the Eye Tribe eye-tracker

The eye tracking experiment on PsychoPy 2 is compatible with the [Eye-Tribe eye-tracker](https://theeyetribe.com/theeyetribe.com/about/index.html).

#### Requirements:
- version of the PsychoPy 1.83.04
- the installed [Eye-Tribe SDK](https://github.com/eyetribe)

The code provides the outlook on the eye-tracking experiment with the given sequence:
- 0.5 s. blanck screen with trigger 1001
- 0.5 s. fixation cross with trigger 2001
- decision with trigger 3001

In case we want to see the **direction of the gaze**, uncomment *draw_gaze_dot* function in each of the above mentioned sequences (namely instructions_blank_screen, instructions_fixation_cross, instructions_choice_decision)

The experiment saves the decision output for n trials (here the number of trials is 2 for the testing purposes), as well as the eye gaze data.

The decision data is organized in the columns as follows:
['Subject_id','Condition', 'Decision', 'Trigger','Item number', 'c1','c2','c3','c4','c5','c6','m1','m2','m3','m4','m5','m6', 'Reaction time', 'Reaction time since decision screen start'],
where 'c1','c2','c3','c4','c5','c6','m1','m2','m3','m4','m5','m6' are the values of the proposed choice in the table for the left and right side respectively.

The decision data is saved in .csv in the format of  "subject_id+'\_decision_output'+localtime", and eye-tracking data is saved as "subject_id+eyetracking_output+localtime".

Instructions can be found in folder Instructions/, as well as the experimental design. Few amendments had been made with respect to the position of the fixation cross, background colour etc., however it shows a good quick overview on the experiment. For more details see *Instructions/Design.pdf*.

## Experiment description

#### Start of the Experiment
- I. Input subjectID (experimenter puts them in before the subjects are seated)
- II. Instruction Slide I (JPEG)
- III. 10 Individual Trial – see attached PDF
- Trigger 1001 Blank screen (500ms)
- Trigger 2001 Fixation cross (500 ms)
- Trigger 3001 Decision Screen (individual decision time)
	- Read in the presented number from the input.csv
	- Activate keys “C” and “M” as response keys
	- Store responses together with “Trigger” in decision_output.csv
	- Store eye-tracking measures together with “Trigger” in eyetracking_output.csv

END Screen that says “Thank you for your participation”

#### Data storage:
##### decision_output.csv
1. subjectID,
2. Response (C or M)
3. Trigger
4. All presented values from input.csv (item etc.)

##### eyetracking_output.csv
1. subjectID,
2. x
3. y
4. gazetime
5. Trigger

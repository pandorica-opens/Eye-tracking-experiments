# The Experiment for the Eye Tribe eye-tracker

The eye tracking experiment on PsychoPy 2 is compatible with the Eye-Tribe eye-tracker https://theeyetribe.com/theeyetribe.com/about/index.html.

Requirements:
- version of the PsychoPy 1.83.04
- the installed Eye-Tribe SDK https://github.com/eyetribe

The code provides the outlook on the eye-tracking experiment with the given sequence:
- 0.5 s. blanck screen with trigger 1001
- 0.5 s. fixation cross with trigger 2001
- decision with trigger 3001

In case we want to see the direction of the gaze, uncomment "draw_gaze_dot" in each of the above mentioned sequences (namely instructions_blank_screen, instructions_fixation_cross, instructions_choice_decision)

The experiment saves the decision output for n trials (here the number of trials is 2 for the testing purposes), as well as the eye gaze data.

The decision data is organized in the columns as follows:
['Subject_id','Condition', 'Decision', 'Trigger','Item number', 'c1','c2','c3','c4','c5','c6','m1','m2','m3','m4','m5','m6', 'Reaction time', 'Reaction time since decision screen start'],
where 'c1','c2','c3','c4','c5','c6','m1','m2','m3','m4','m5','m6' are the values of the proposed choice in the table for the left and right side respectively.

The decision data is saved in .csv in the format of  "subject_id+'_decision_output'+localtime", and eye-tracking data is saved as "subject_id+eyetracking_output+localtime".

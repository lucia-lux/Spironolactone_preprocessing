# Spironolactone_preprocessing
Preprocess qualtrics files and HRV time stamps.
Check for likely double tags in E4 files (and therefore, participants who may have missed a tag).

A general note:
Jupyter notebooks contain all utilities functions and analysis code + markup and are written in a tutorial-style way (-ish).
If anything remains unclear, I am happy to help, just let me know.
the preprocess_modules folder contains the utilities modules for the .py versions of the analysis code.
The .py files in the main folder contain that analysis code, and utilities functions are imported (so you won't have everything in one place).
If you would like to get an idea of how things work, then I recommend looking at the Jupyter notebooks.

Diary files preprocessing:
The goal here is to clean up known issues (participants reporting no intrusions, but providing distress/vividness ratings) and make the files a bit nicer to work with by renaming columns etc.
As per request, I have made preprocessing steps that result in removal of a given record optional. You will be asked for user input at the relevant stages (y/n to removal).

HRV files:
The goal was to identify sections of the HRV files that correspond to specific events. For more information on the approach taken, please see the Jupyter notebook.
This program does not currently check E4 files for cases where qualtrics time captures might be missing. The main reason for this is that I haven't encountered this problem in the existing file and so finding the right file and tag didn't seem worth it. If this is something you feel you need/would like to incorporate, I'm happy to add this, or help you add it (or just branch and add it!).

E4 files:
This is to check for likely double tags in the tags.csv file that is generated for each participant.
Basically, the following functionality is included:
- Retrieves tags.csv for each participant and does some basic checks (>1 folder for a given participant; tags file missing; < minimum number of expected tags - should have at least 14 without intrusions).
- prints any participant numbers for whom problems have been detected and stores these numbers in a list so you can inspect further
- gets the difference in tag times between successive rows and looks for the smallest such difference for each participant. This is based on the idea that double tags are suppose to happen in quick succession, with no other tag happening that quickly.
- Looks for tag times in the range up to min_difference+a threshold. This threshold is defined by multiplying min_difference by a range of values and testing at which point we are able to detect the largest number of 2 double tags (read that again :). This is obviously not perfect, but the reasoning is that most participants will likely double tag twice in accordance with instructions. By setting the threshold to maximize the number of participants for which 2 double tags have been detected, we are therefore likely to catch those people who may have had issues with their E4 tags.
- If you run the script, it will print out a list of participants that should be checked manually (due to missing tag files, duplicate records, fewer than the expected number of tags or session notes on E4 stuff recorded)
- It will also print out a list of participant numbers for whom fewer or more than the expected number of double tags were detected.
The above will hopefully help cut down the number of participants for whom manual tag file inspections are required.

Happy analysing, CPU crew.


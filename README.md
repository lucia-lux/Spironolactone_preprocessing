# Spironolactone_preprocessing
Preprocess qualtrics files and HRV time stamps.

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

Happy analysing, CPU crew.


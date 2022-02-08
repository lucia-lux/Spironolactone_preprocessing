# main script for preprocessing diary files.
import os
import pandas as pd
import numpy as np
import preprocess_modules.utilities as utils

#specify path to input dir and read in files using identifier ('diary')
input_dir = r"P:\Spironolactone\preprocess_dat"
input_files = [file for file in os.listdir(input_dir) if 'diary' in file]

# make output dir
output_dir = os.path.join(input_dir,"processed_diaries")
try:
    os.makedirs(output_dir)
except OSError:
    # if directory already exists
    pass

# save to output dir?
save = 1
for file in input_files:
    diary_file = pd.read_csv(os.path.join(input_dir,file),skiprows = [0,2])
    diary_file = utils.preprocess_frame(diary_file, 'Finished',["Start Date","Participant number:","Start time (HH:MM):"],"had_intrusions")
    carry_on = input("If you proceed, some cleaning processes will be applied and the data will be written to a file. Continue? Y/N\n")
    if carry_on.lower()==("y"):
        diary_file = utils.rem_dat_no_ints(diary_file)
        if save:
            diary_file.to_csv(os.path.join(output_dir, '_'.join([file[:-4],'processed.csv'])),index = False)
        else:
            pass

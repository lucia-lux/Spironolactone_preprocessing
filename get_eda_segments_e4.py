import os
import re
import warnings
import pandas as pd
import numpy as np
from preprocess_modules import utilities_hrv as hrvutils
from preprocess_modules import utilities_e4 as e4utils


# paths to input directories
e4_dir = r"P:\Spironolactone\E4"
main_dir = r"P:\Spironolactone\main_qualtrics"
main_filename = "main_dat21.csv"
participant_folders = os.listdir(e4_dir)
# get relevant folders from E4 direcotries
participant_folders = [f for f in participant_folders if re.search("^p[0][0-9][0-9]",f.lower())]

# make output directory
output_dir = os.path.join(e4_dir,"processed_e4_files")
try:
    os.mkdir(output_dir)
except OSError:
    # if directory already exists
    warnings.warn("Directory already exists. Files may be overwritten. Manual check advised.")

# read in qualtrics file
col_list =  ["Status","DQ-1","Firstbeat_on_time","baseline start","baseline end","Q645","Q646","FILM-START","Q648","Q649"]
new_names = ["Response_type","Participant_number","Firstbeat_start","RT1_start","RT1_end","RT2_start","RT2_end","Film_start","RT3_start","RT3_end"]
qualtrics_df = pd.read_csv(os.path.join(main_dir,main_filename),usecols =col_list,skiprows= [1,2])
qualtrics_df.columns = new_names

# make interval cols
qualtrics_df = hrvutils.remove_invalid_records(qualtrics_df,"Participant_number",exclude_pnums = [1])
duplicates = hrvutils.flag_duplicate_participants(qualtrics_df,"Participant_number")
qualtrics_df = hrvutils.remove_duplicate_participants(qualtrics_df,"Participant_number")
qualtrics_df = hrvutils.convert_time_cols(qualtrics_df)
qualtrics_df = hrvutils.add_end_time(qualtrics_df,"Film_start",15)
rt_time_cols = [f for f in qualtrics_df.columns if any(k in f for k in ["start","end"])]
for rt_time in rt_time_cols[1:]:
    qualtrics_df = hrvutils.make_rel_time_cols(qualtrics_df,rt_time_cols[0],rt_time)
qualtrics_df = hrvutils.convert_to_secs(qualtrics_df)

start_intervals = qualtrics_df.filter(like = "start_interval", axis = 1).columns.sort_values()
end_intervals = qualtrics_df.filter(like = "end_interval", axis = 1).columns.sort_values()
intervals = list(zip(start_intervals, end_intervals))
qualtrics_pnums = qualtrics_df.Participant_number.values

missing_eda = []
pnums = []
eda_dat = []
below_min = []
missing_sec = []
duplicates = e4utils.flag_duplicates(participant_folders)
# somewhat arbitrary. If length of EDA recording indicates that session<4 hours, flag this.
# the formula for calculating min_session_length is: hours*minutes_per_hour*seconds_per_minute*sampling_rate
min_session_length = 4*60*60*4


for folder in participant_folders:
    pnum = e4utils.get_participant_num(folder)
    if pnum not in qualtrics_pnums:
        print(f" Participant {pnum} not in qualtrics file. Skipping.")
        continue
    if pnum in duplicates:
        print(f"More than one file exists for participant {pnum}. Skipping.")
        continue
    try:
        eda_df = pd.read_csv(os.path.join(e4_dir,folder,"EDA.csv"),header = None,names = ["EDA"])
    except FileNotFoundError:
        print(f"No E4 file found for participant {pnum}.Manual check advised.")
        missing_eda.append(pnum)
        continue
    if eda_df.shape[0]<min_session_length:
        print(f"Recording for participant {pnum} seems short. Manual check advised.")
        below_min.append(pnum)
        continue
    for start, stop in intervals:
        start_val = qualtrics_df.loc[qualtrics_df.Participant_number == pnum,start]
        stop_val = qualtrics_df.loc[qualtrics_df.Participant_number == pnum,stop]
        try:
            [int(val) for val in [start_val, stop_val]]
        except (ValueError, TypeError) as e:
            print(f"At least one of start_val, stop_val not int. Skipping participant {pnum}.")
            continue
        interval_df = e4utils.get_eda_intervals(eda_df,start_val,stop_val,4)
        if interval_df.empty:
            interval_name = start.split("_")[0]
            warnings.warn(f"Participant {pnum} has no valid data for {interval_name} interval.\nManual check advised.")
            missing_sec.append([pnum,interval_name])
            continue
        # save to file
        interval_df.to_csv(os.path.join(output_dir, "_".join([start.split("_")[0],str(int(pnum)),"eda.csv"])),index = False)
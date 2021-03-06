import os
import re
from datetime import datetime
import pandas as pd
import numpy as np
from preprocess_modules import utilities_e4 as e4
from preprocess_modules import utilities_hrv as hrvutils
from preprocess_modules import utilities as dutils

input_dir = r"P:\Spironolactone\E4"
main_dir = r"P:\Spironolactone\main_qualtrics"
participant_folders = os.listdir(input_dir)
participant_folders = [f for f in participant_folders if re.search("^p[0][0-9][0-9]",f.lower())] 

# get relevant cols from the main qualtrics session file
col_list =  ["Status","Finished","DQ-1","Firstbeat_on_time", "MUSIC-T1"]
new_names = ["response_type","finished","participant_number","firstbeat_start","music_start"]
qualtrics_df = pd.read_csv(os.path.join(main_dir,"main_dat.csv"),usecols =col_list,skiprows= [1,2])
qualtrics_df.columns = new_names
qualtrics_df = hrvutils.remove_invalid_records(qualtrics_df, "participant_number",[1])
qualtrics_df = dutils.remove_incomplete_rows(qualtrics_df, "finished")
qualtrics_df = qualtrics_df.drop(labels = ["response_type","finished"], axis = 1)
# get time difference between qualtrics firstbeat on and music start time stamps
qualtrics_df = hrvutils.convert_time_cols(qualtrics_df)
qualtrics_df["time_delta"] = qualtrics_df["music_start"]- qualtrics_df["firstbeat_start"]

# load tag file for each participant and construct tags dataframe
missing_tags = []
pnums = []
tags_dat = []
duplicates = e4.flag_duplicates(participant_folders)
below_min = []

for folder in participant_folders:
    pnum = e4.get_participant_num(folder)
    if pnum in duplicates:
        print(f"More than one tag file exists for participant {pnum}. Skipping.")
        continue
    try:
        tags_df = pd.read_csv(os.path.join(input_dir,folder,"tags.csv"),header = 0,names = [pnum])
    except FileNotFoundError:
        print(f"No tags file found for participant {pnum}.Manual check advised.")
        missing_tags.append(pnum)
        continue
    if tags_df.shape[0]<14:
        print(f"Participant {pnum} recorded fewer than the minimum number of tags. Manual check advised.")
        below_min.append(pnum)
        continue
    pnums.append(pnum)
    tags_dat.append(tags_df)

tags_df = pd.concat(tags_dat,axis = 1,keys =[pnum for pnum in pnums])
tags_df = e4.remove_multindex(tags_df,1,1)


tags_diff_df = tags_df.apply(lambda x: e4.get_rowdiff(x))
min_deltas = e4.find_min_delta(tags_diff_df)
thresholds = np.arange(1.5,5,0.5)
all_tag_vals = []
for thresh in thresholds:
    double_df = e4.return_likely_doubles(min_deltas, tags_diff_df, thresh)
    tag_vals = e4.get_num_double_tags(double_df)
    num_twos = tag_vals[2]
    all_tag_vals.append((num_twos,thresh))
max_thresh = e4.get_best_thresh(all_tag_vals)
double_df = e4.return_likely_doubles(min_deltas, tags_diff_df,max_thresh)
detect_missing_doubles_df = e4.detect_missing_doubles(double_df)

double_df["Events"] = pd.Series([
                                "Firstbeat","RT1_start","RT1_end","Drug",
                                "RT2_start","RT2_end","Film_start","Film_end",
                                "RT3_start","RT3_end","DT1_music_starts",
                                "DT2_music_starts"
                                ])

single_tags = e4.check_double_tags(double_df,1)
print(double_df[double_df.Events.isin(["DT1_music_starts","DT2_music_starts"])])

qualtrics_df = pd.read_csv(os.path.join(main_dir,"main_dat.csv"),skiprows = [1,2],usecols = ["DQ-1", "NOTES"])
qualtrics_df.columns = ["pnum","session_notes"]
qualtrics_df = qualtrics_df.drop(labels = qualtrics_df[qualtrics_df.session_notes.isna()].index, axis = 0)
keywords = ["tag","e4"]
flagged_participants = e4.find_e4_notes(qualtrics_df,"session_notes","pnum",keywords)

manual_check_pnums = e4.check_pnums(flagged_participants,missing_tags,below_min,duplicates)
print(f"\nThe following participants had fewer or more than the expected number of double tags:\n{[num for num in detect_missing_doubles_df.pnum]}\n")
print(f"\nThe following participants are worth checking manually:\n{manual_check_pnums}")
print("\nA breakdown of reasons:")
print(f"duplicates:\n{duplicates}")
print(f"missing tag files:\n{missing_tags}")
print(f"fewer than min tags (14):\n{below_min}")
print(f"session notes mention E4:\n{flagged_participants}")
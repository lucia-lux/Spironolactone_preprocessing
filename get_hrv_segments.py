import os
import datetime
import pandas as pd
import numpy as np
import warnings
from preprocess_modules import utilities_hrv

main_dir = r"P:\Spironolactone\main_qualtrics"
hrv_dir = r"P:\Spironolactone\Firstbeat"
hrv_files = [file for file in os.listdir(hrv_dir) if file.lower().startswith('p') and file.endswith('.csv')]

output_dir = os.path.join(hrv_dir,"processed_hrv_files")
try:
    os.makedirs(output_dir)
except OSError:
    # if directory already exists
    warnings.warn("Directory already exists. Files may be overwritten. Manual check advised.")
    pass

col_list =  ["Status","DQ-1","Firstbeat_on_time","baseline start","baseline end","Q645","Q646","FILM-START","Q648","Q649"]
new_names = ["response_type","participant_number","Firstbeat_start","RT1_start","RT1_end","RT2_start","RT2_end","Film_start","RT3_start","RT3_end"]
qualtrics_df = pd.read_csv(os.path.join(main_dir,"main_dat.csv"),usecols =col_list,skiprows= [1,2])
qualtrics_df.columns = new_names

qualtrics_df = utilities_hrv.remove_invalid_records(qualtrics_df, "participant_number",exclude_pnums = [1])
duplicates = utilities_hrv.flag_duplicate_participants(qualtrics_df,"participant_number")
qualtrics_df = utilities_hrv.remove_duplicate_participants(qualtrics_df,"participant_number")
qualtrics_df = utilities_hrv.convert_time_cols(qualtrics_df)
qualtrics_df = utilities_hrv.add_end_time(qualtrics_df,"Film_start",15)
rt_time_cols = [f for f in qualtrics_df.columns if any(k in f for k in ["start","end"])]
for rt_time in rt_time_cols[1:]:
    qualtrics_df = utilities_hrv.make_rel_time_cols(qualtrics_df,rt_time_cols[0],rt_time)
qualtrics_df = utilities_hrv.convert_to_secs(qualtrics_df)

# Zip up start/end interval column names for easier access in for loop below:
start_intervals = qualtrics_df.filter(like = "start_interval", axis = 1).columns.sort_values()
end_intervals = qualtrics_df.filter(like = "end_interval", axis = 1).columns.sort_values()
intervals = list(zip(start_intervals, end_intervals))

# Track participants whose HRV data for any of the intervals is missing
missing_pnums = []
for pnum in qualtrics_df.participant_number:
    # check if file exists
    try:
        my_rec = utilities_hrv.select_hrv_record(pnum,hrv_files)
    except IndexError:
        print(f"No HRV file found for participant {pnum}.")
        continue
    # read in HRV file for participant pnum
    hrv_df = pd.read_csv(
                        os.path.join(hrv_dir,my_rec),
                        header = 0, names = ["IB_intervals"],
                        skiprows = np.arange(0,4)
                        )
    # select the part of the HRV file that corresponds to given interval
    # do this for all intervals (Film, RT1, RT2, RT3)
    for start_interval, end_interval in intervals:
        start_time = utilities_hrv.get_time_stamp(qualtrics_df,"participant_number", start_interval, pnum)
        end_time = utilities_hrv.get_time_stamp(qualtrics_df,"participant_number", end_interval, pnum)
        interval_df = utilities_hrv.get_hrv_interval(hrv_df,start_time,end_time)
        # if the resulting dataframe is empty, flag this and hold on to pnum/interval
        if interval_df.empty:
            interval_name = start_interval.split("_")[0]
            warnings.warn(f"{pnum} has no valid data for {interval_name} interval.\nManual check advised.")
            missing_pnums.append([pnum,interval_name])
            continue
        # save to file
        interval_df.to_csv(os.path.join(output_dir, "_".join([start_interval.split("_")[0],str(int(pnum)),"hrv.csv"])),index = False)
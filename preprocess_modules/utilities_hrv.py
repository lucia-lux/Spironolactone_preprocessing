import datetime
import warnings
import pandas as pd

def remove_invalid_records(in_df, exclude_pnums = None):
    """
    remove invalid records - participant id is nan or
    >100 (usually indicates test record)

    Parameters
    ----------
    in_df:  pd DataFrame
        dataframe to operate on
    exclude_pnums: list[int]
        specify participants who should be 
        excluded from the analysis, if any

    Returns
    -------
        dataframe w/o the above records
    """
    in_df = in_df[(in_df.Participant_number.notna())
                    &(in_df.Participant_number<100)]
    if exclude_pnums:
        in_df = in_df.drop(labels = in_df[
                in_df.Participant_number.isin(exclude_pnums)].index,
                axis = 0)
    return in_df
    
def remove_duplicate_participants(in_df):
    """
    If we have duplicate records
    for a given participant, remove
    that with the most NaNs.

    Parameters
    ----------
    in_df:  pd Dataframe

    Returns
    -------
        in_df w/o all nan duplicates
    """
    duplicated = in_df.loc[in_df.duplicated(subset = "Participant_number"),"Participant_number"]
    if duplicated is None:
        return in_df
    else:
        drop_inds = []
        for dup in duplicated:
            nan_sum = in_df[in_df.Participant_number == dup].isna().sum(axis = 1)
            nan_max_ind = nan_sum[nan_sum == nan_sum.max()].index
            drop_inds.append(nan_max_ind[0])
        in_df = in_df.drop(labels = drop_inds, axis = 0)
        return in_df       

def flag_duplicate_participants(in_df):
    """
    If we have duplicate records
    for a given participant, flag
    them.

    Parameters
    ----------
    in_df:  pd Dataframe

    Returns
    -------
        participant numbers for those
        with duplicate records
    """
    duplicated = in_df.loc[in_df.duplicated(subset = "Participant_number"),"Participant_number"]
    print(f"The following participants have duplicate records:\n{duplicated.values}")
    return duplicated         

def convert_time_cols(in_df):
    """
    convert time cols to datetime format
    
    Parameters
    ----------
    in_df:  pd Dataframe
        dataframe to operate on
    
    Returns
    -------
    dataframe with time cols converted
    to datetime format.
    """
    time_cols = [col for col in in_df.columns
                if any(k in col for k in ["start","end"])]
    in_df.loc[:,time_cols] = in_df.loc[:,time_cols].apply(
                                lambda x: pd.to_datetime(x,errors = "coerce"),
                                axis = 1)
    return in_df

def add_end_time(in_df,start_time_col, amount):
    """
    If we don't have a time for the interval end,
    provide an end time in minutes from start time.

    Parameters
    ----------
    in_df:  pd dataframe
        dataframe to operate on
    start_time_col: str
        name of column with interval start time
        eg. Film_start
    amount: int
        number of minutes to add to start time
    
    Returns
    -------
    in_df with end_time column added.
    """
    new_col_name = "_".join([start_time_col.split("_")[0],"end"])
    in_df[new_col_name] = in_df[start_time_col] + datetime.timedelta(minutes = amount)
    return in_df

def make_rel_time_cols(in_df,time_col_start,time_col_end):
    """
    calculate relative timings for time columns.

    Parameters
    ----------
    in_df:  pandas Dataframe
        dataframe to operate on
    time_col_start: str
        name of start time column
    time_col_end:   str
        name of end time column
    
    Returns
    -------
    in_df with rel time columns added
    """
    new_col_name = "_".join([time_col_end,"interval"])
    in_df[new_col_name] = in_df[time_col_end]-in_df[time_col_start]
    return in_df

def convert_to_secs(in_df):
    """
    convert time delta to seconds.

    Parameters
    ----------
    in_df:  pd Dataframe
        dataframe to operate on
    
    Returns
    -------
    interval cols converted to secs
    from Firstbeat start time.
    """
    interval_cols = in_df.filter(like = "interval",axis = 1).columns
    in_df.loc[:,interval_cols] = in_df.loc[:,interval_cols].applymap(
                                            lambda x: x.total_seconds())
    return in_df

def select_hrv_record(pnum,hrv_files):
    """
    select hrv file for participant
    
    Parameters
    ----------
    pnum:   int or float
        participant number whos record
        needs to be retrieved
    hrv_files:  list[str]
        list of hrv files
    
    Returns
    -------
        name of hrv file for participant pnum (str)
    """
    recs = [file for file in hrv_files if int(file[1:4])==pnum]
    if len(recs)>1:
        warnings.warn(f"Found more than one file for participant {pnum}.\nManual check advised.")
    return recs.pop()

def get_time_stamp(in_df,interval_col,pnum):
    """
    Get time stamp for processing HRV files.

    Parameters
    ----------
    in_df:  pd Dataframe
        input dataframe
    interval_col:   str
        name of column with desired interval
        eg "Film_start_interval"
    pnum:   int
        participant number
    
    Returns
    -------
    time stamp (for input to get_hrv_interval())
    """
    time_stamp = in_df[in_df.Participant_number==pnum].reset_index().at[0,interval_col]
    return time_stamp

def get_hrv_interval(hrv_df,interval_start:float,interval_end:float):
    """
    Get intervals for HRV data
    This function will find the closest value to the
    specified start and end times.

    Parameters
    ----------
    hrv_df: pd DataFrame
        HRV data for a given participant
    interval_start: float
        start time as duration in seconds from
        start of Firstbeat (ie Film_start for participant 1)
    interval_end:   float

    """
    hrv_df["IBI_cumsum"] = hrv_df.IB_intervals.cumsum()/1000
    start_vals = (hrv_df.IBI_cumsum-interval_start).sub(0).abs().idxmin()
    end_vals = (hrv_df.IBI_cumsum-interval_end).sub(0).abs().idxmin()
    interval_df = hrv_df.iloc[start_vals:end_vals]
    return interval_df["IB_intervals"]
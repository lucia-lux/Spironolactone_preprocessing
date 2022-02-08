# utilities

import numpy as np
import re

def remove_incomplete_rows(in_df,finished_col):
    """
    remove rows containing incomplete records
    
    Parameters
    ----------
    in_df:  pd DataFrame
        input dataframe to operate on
    finished_col:   str
        name of column containing complete/incomplete info
        NB: looking for the col with BOOLEAN not %
    Returns
    -------
        df w/o incomplete records
    """
    in_df = in_df[in_df[finished_col]==True]
    return in_df

def flag_incomplete_rows(in_df,finished_col):
    """
    flag rows containing incomplete records
    
    Parameters
    ----------
    in_df:  pd DataFrame
        input dataframe to operate on
    finished_col:   str
        name of column containing complete/incomplete info
        NB: looking for the col with BOOLEAN not %
    Returns
    -------
        participant numbers associated with incomplete rows
    """
    participants = in_df.loc[in_df[finished_col]==False,'Participant number:']
    if len(participants)<1:
        print("No incomplete records in file.")
    else:
        print(f"The following participants have incomplete records:{participants}")
    return participants


def rename_diary_cols(in_df, start_phrase = None, col_num = None):
    """
    Rename the columns referring to diary content
    Parameters
    ----------
    in_df:  pd DataFrame
        input dataframe to operate on
    start_phrase:   str
        phrase to look for in column name
    col_num:    str
        column marker, eg "column 1"
    """
    if col_num is None:
        in_df = in_df.rename(columns = {in_df.filter(like = start_phrase, axis = 1).columns[0]: "had_intrusions"})
    else:
        if "1" in col_num:
            new_names = ['_'.join(['content',str(num)]) for num in np.arange(1,13)]
        elif "2" in col_num:
            new_names = ['_'.join(['freq',str(num)]) for num in np.arange(1,13)]
        elif "3" in col_num:
            new_names = ['_'.join(['distress',str(num)]) for num in np.arange(1,13)]
        else:
            new_names = ['_'.join(['vivid',str(num)]) for num in np.arange(1,13)]
        
        old_names = in_df.filter(like = col_num.upper(), axis = 1).columns
        in_df.rename(columns = dict(zip(old_names,new_names)),inplace = True)
    return in_df

def flag_ints_notyesno(in_df,int_col):
    """
    Check if some participants responded something
    other than yes or no for the 'Did you have intrusions?"
    question.

    Parameters
    ----------
    in_df:  pd DataFrame
        dataframe to operate on
    int_col:    str
        Name of the intrusion column question as a string
    Returns
    -------
    Participant numbers for people who did not respond yes/no.
    """
    participants = in_df.loc[~in_df[int_col].isin(["Yes","No"]),'Participant number:']
    print(f"The following participants did not make a yes or no response:\n{participants.values}")
    return participants

def select_columns(in_df, select_list):
    """
    Select columns to process.
    NB: This is to specify columns in addition
    to the intrusion-related ones (eg date, time, etc)
    
    Parameters
    ----------
    in_df:  pd DataFrame
        dataframe to operate on
    select_list: list[str]
        names of columns to retain
    Returns
    -------
    in_df w/o irrelevant columns
    """
    diary_cols = [f for f in in_df.columns
                    if any
                    (k in f for k in 
                    ["had_intrusions","content","freq","distress","vivid"])]
    select_list.extend(diary_cols)
    in_df = in_df.loc[:,select_list]
    return in_df

def strip_col_names(in_df):
    """
    strip col names for easier handling
    
    Paramters
    ---------
    in_df:  pd dataframe
        dataframe to operate on
    
    Returns
    -------
        in_df w stripped col names
    """
    in_df.columns = [f.lower().strip(":") for f in in_df.columns]
    in_df.columns = [re.sub("[\(\[].*?[\)\]]", "", f)for f in in_df.columns]
    in_df.columns = [f.strip() for f in in_df.columns]
    in_df.columns = [f.replace(" ","_") for f in in_df.columns]
    return in_df

def preprocess_frame(in_df,finished_col,select_list,int_col):
    """
    preprocess dataframe
    This just strings together some of the other functions.
    You can customize by shuffling the steps or adding your own.
    
    Parameters
    ----------
    in_df:  pd DataFrame
        dataframe to operate on
    finished_col:   str
        name of column indicating whether they completed the survey
    select_list:    list[str]
        list of column names to retain (in addition to intrusion related ones)
    int_col:    str
        name of column with intrusions yes/no answer
    """
    pnums_incomplete = flag_incomplete_rows(in_df,'Finished')
    remove_recs = input("Would you like to participants with incomplete records? Y/N\n")
    if remove_recs.lower() == "y":
        in_df = remove_incomplete_rows(in_df,finished_col)
    else:
        pass
    in_df = rename_diary_cols(in_df, start_phrase = "have you experienced")
    pnums_notyn = flag_ints_notyesno(in_df,int_col)
    col_nums = [' '.join(['column',str(num)]) for num in np.arange(1,5)]
    for col in col_nums:
        in_df = rename_diary_cols(in_df,col_num = col)
    in_df = select_columns(in_df,select_list)
    in_df = strip_col_names(in_df)
    pnums_noint = flag_dat_no_cont(in_df)
    return in_df
    
def rem_dat_no_ints(in_df, set_val = np.nan):
    """
    Remove data for records w/out intrusions
    if had_intrusions == "No",
    set vivid/distress to NaN
    If other value is preferable, this can be
    supplied as an additional input parameter
    (see below)

    Parameters
    ---------
    in_df:  pd DataFrame
        input dataframe to operate on
    set_val:
        Replace content in distress/vividness cols
        with this value. Default is NaN.
    Returns
    -------
        in_df w data modified
    """
    diary_cols = [col for col in in_df.columns if 
                    any(name in col for name in
                    ['distress','vivid'])]
    inds = in_df.loc[in_df.had_intrusions=='No',diary_cols].dropna(how = "all")
    in_df.loc[inds.index,diary_cols] = set_val
    return in_df

def flag_dat_no_cont(in_df):
    """
    Flag data for records with had_intrusions == "No",
    but provided content and ratings.

    Parameters
    ---------
    in_df:  pd DataFrame
        input dataframe to operate on
    Returns
    -------
        participant numbers for people who
        responded no, but supplied content/ratings
    """
    content_cols = in_df.filter(like = "content",axis = 1).columns.values
    response_no_df = in_df.loc[in_df.had_intrusions=="No",content_cols]
    response_no_df["participant_number"] = in_df["participant_number"]
    response_no_df = response_no_df.set_index("participant_number")
    response_no_df = response_no_df[~response_no_df.isin(["0",0])].dropna(how = "all")
    participants = response_no_df.index
    print(f"The following participants reported no intrusions, but provided content:\n{participants.values}")
    return participants
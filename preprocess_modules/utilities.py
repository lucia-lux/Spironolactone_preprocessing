# utilities

import numpy as np

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

def select_columns(in_df, select_list):
    """
    Select columns to process.
    
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
    in_df.columns = [f.strip(":") for f in in_df.columns]
    in_df.columns = [f.replace(" ","_") for f in in_df.columns]
    return in_df

def preprocess_frame(in_df,finished_col,select_list):
    """ preprocess dataframe"""
    in_df = remove_incomplete_rows(in_df,finished_col)
    in_df = rename_diary_cols(in_df, start_phrase = "have you experienced")
    col_nums = [' '.join(['column',str(num)]) for num in np.arange(1,5)]
    for col in col_nums:
        in_df = rename_diary_cols(in_df,col_num = col)
    in_df = select_columns(in_df,select_list)
    in_df = strip_col_names(in_df)
    return in_df

def rem_dat_no_ints(in_df):
    """
    Remove data for records w/out intrusions
    if had_intrusions == "No",
    set content/vivid/freq/distress to NaN

    Parameters
    ---------
    in_df:  pd DataFrame
        input dataframe to operate on
    Returns
    -------
        in_df w data modified
    """
    diary_cols = [col for col in in_df.columns if 
                    any(name in col for name in
                    ['distress','vivid'])]
    in_df.loc[in_df.had_intrusions=='No',diary_cols] = np.nan
    return in_df
import re
from collections import Counter
from datetime import datetime


def get_participant_num(folder_name):
    """
    Get participant number from folder
    name.

    Parameters
    ----------
    folder_name:    str
        Name of participant e4 data folder

    Returns
    -------
    Participant number as an integer value.

    """
    pnum = re.findall("p[0][0-9][0-9]",folder_name.lower())
    return int(pnum.pop()[1:])

def flag_duplicates(folder_name):
    """
    Flag duplicate E4 folders.
    Happens when E4 recording was
    interrupted for some reason.

    Parameters
    ----------
    folder_name:    str
    Name of participant e4 data folder

    Returns
    -------
    list of duplicate participant numbers.
    """
    parts = [num[:4] for num in folder_name]
    dups = [int(num[1:]) for num, count in Counter(parts).items() if count>1]
    return dups

def remove_multindex(in_df, axis, level):
    """
    Remove multi index of specified level
    along specified axis.

    Parameters
    ----------
    in_df:  pd DataFrame
        df to operate on
    axis:   int
        rows = 0
        cols = 1
    level:  int
        level of multindex to remove.
    
    Returns
    -------
    dataframe with specified level of multiindex
    removed
    """
    if axis == 0:
        out_df = in_df.reset_index(level = level, drop = True)
    else:
        out_df = in_df.T.reset_index(level = level, drop = True).T
    return out_df
    
def get_rowdiff(values):
    """
    calculate difference
    between rows of series

    Paramters
    ---------
    values

    Returns
        differences between successive
        rows
    """
    if len(values)<=1:
        return values
    else:
        new_vals = []
        for i,val in enumerate(values):
            if i==0:
                new_val = val
            else:
                new_val = val-values[i-1]
            new_vals.append(new_val)
    return new_vals

def find_min_delta(tag_deltas, axis = 0):
    """
    find minimum difference
    between successive tags.

    Parameters
    ----------
    tag_deltas: pd DataFrame
        dataframe of row-to-row differences
    axis:   int
        0 for min row  w/in col
        1 for min col w/in row
    
    Returns
    -------
        min value for each column (participant)
    """
    min_diffs = tag_deltas.apply(lambda x: min(x),axis = axis)
    return min_diffs

def return_likely_doubles(min_deltas, time_delta_df, threshold):
    """
    find likely double tags
    based on min delta

    Parameters
    ----------
    min_deltas: pd Series
        minimum difference between rows
        for each participant
    time_delta_df:  pd DataFrame
        dataframe representing differences
        between successive rows
    threshold:  float
        min_deltas will be multiplied by
        threshold to define an acceptable
        window for identifying double tags
        eg: look for row differences less than
        1.5*min_deltas, where 1.5 would represent
        thresh

    Returns
    -------
        time_delta_df masked with nan where
        threshold exceeded. Non-nan values
        represent possible double tags.
    """
    double_tag_df = time_delta_df[
                                time_delta_df<=min_deltas*threshold
                                ].dropna(how = "all",axis = 0)
    return double_tag_df

def get_num_double_tags(double_tag_df):
    """
    Get number of double tags
    detected in dataframe.

    Parameters
    ----------
    double_tag_df:  pd DataFrame
        dataframe with value for likely
        double tags, NaN elswhere
    
    Returns
    -------
    value counts of double tags identfied
    """
    double_counts = double_tag_df.apply(
                                        lambda x:
                                        x.notna().sum()
                                        ).value_counts()
    return double_counts

def get_best_thresh(tag_val_counts):
    """
    get threshold that maximises
    number of double tags detected

    Parameters
    ----------
    tag_val_counts: list of tuples
        of type [(two_counts, threshold)]
    
    Returns
    -------
        Threshold at which max number of 
        two double tags were detected.

    """
    max_num = max([val[0] for val in tag_val_counts])
    max_threshold = [thresh for (num,thresh)
                    in tag_val_counts if num == max_num]
    if len(max_threshold)>1:
        print(f"More than 1 max val detected. Manual check advised.")
    return max_threshold

def detect_missing_doubles(double_tags_df):
    """
    Flag participants with (possible)
    missing double_tags.

    Parameters
    ----------

    Returns
    -------
    """
    num_tags = double_tags_df.apply(
                                    lambda x: len(x.dropna())
                                    )
    flags_df = num_tags[num_tags != 2]
    flags_df = flags_df.reset_index()
    flags_df.columns = ["pnum","num_double_tags"]
    return flags_df


def check_pnums(*args):
    """
    Get a single list of all
    pnums worth double checking
    for any reason (duplicates,
    <min tags, qualtrics notes detected)

    Parameters
    ----------
    args:   list
        lists of participant numbers
        for which problems have been
        detected.
        Eg: duplicates, below_min
    
    Returns
    -------
    A single list of participant numbers
    to check.
    """
    all_pnums = []
    for arg in args:
        all_pnums.extend(arg)
    return set(all_pnums)

def find_e4_notes(study_session_df,notes_col, pnum_col, keywords):
    """
    Get participant numbers for whom E4 related
    issues were flagged in the data acquisition 
    session.

    Parameters
    ----------
    study_session_df:   pd DataFrame
        data frame containing main study session
        data. Must have participant number and session
        notes.
    notes_col, pnum_col:    str
        names of session notes/participant number columns
    keywords:   list[str]
        a list of strings representing keywords to look for
        in the session notes.
    
    Returns
    -------
    participant numbers for whom E4 related events were recorded
    in the session notes.
    """
    reg_substr = "|".join(keywords)
    flagged_participants = study_session_df.loc[study_session_df[
                            notes_col].str.lower().str.contains(reg_substr),
                            pnum_col].astype(int).values
    return flagged_participants

def check_double_tags(double_tag_df, num_tags):
    """
    This function lets you inspect participants
    with unusual double tag numbers (below or above
    2).

    Parameters
    ----------
    double_tag_df:  pd DataFrame
        dataframe of likely double tags
    num_tags:   int
                the number of tags to look for
                eg 1, 3, 4...
    
    Returns
    -------
    A dataframe showing only cols for participants
    with the specified number of double tags.
    OR
    if no participants found for the specified number
    of tags, this function will return None.
    """

    double_view_df = double_tag_df.loc[
                                        :,double_tag_df.notna().sum()==num_tags
                                        ]
    if double_view_df.shape[1]<=1:
        print("No participants found for this number of tags.")
    else:
        return double_view_df


def get_only_time(in_df, time_cols:list[str]):
    """
    get time only from datetime cols.

    Parameters
    ----------
    in_df:  pd Dataframe
        input dataframe
    time_cols:  list[str]
        names of columns to convert
    
    Returns
    -------
    in_df with only time in time_cols
    """
    in_df = in_df.loc[:,time_cols].applymap(
            lambda x: datetime.strptime(x,"%H:%M").time())
    return in_df
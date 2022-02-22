import re


def select_columns_main(in_df, select_list):
    """
    Select columns to process.
    Main qualtrics version.
    
    Parameters
    ----------
    in_df:  pd DataFrame
        dataframe to operate on
    select_list: list[str]
        names of columns to retain
    Returns
    -------
    in_df with only specified columns
    """
    in_df = in_df.loc[:,select_list]
    return in_df

def remove_newlines(in_df, rounds = 1):
    """
    Remove newlines from text.
    if rounds = 1, just remove leading
    and trailing newlines
    if rounds > 1, additionally replace
    newlines in text with whitespace.

    Parameters
    ----------
    in_df:  pd DataFrame
        input dataframe
    rounds: int
        1 or more rounds, see above
    
    Returns
    -------
    in_df with newlines removed
    """
    if rounds == 1:
        in_df = in_df.applymap(lambda x: x.strip())
    else:
        in_df = in_df.applymap(lambda x: x.strip())
        in_df = in_df.applymap(lambda x: x.replace("\n", " "))
    return in_df

def make_dict(keys, values):
    """
    Make dicts for questionnaire scoring

    Parameters
    ----------
    keys:   list[str]
        string values of questionnaire
        scores as they appear in qualtrics
    values: list[int]
        the scores corresponding to the
        string values in keys
    
    Returns
    -------
        dict containing string values as keys
        and ints for replacement as values.
    """
    keys = [key.lower() for key in keys]
    my_key_dict = dict(zip(keys,values))
    return my_key_dict

def filter_cols(in_df, substr):
    """
    filter for relevant columns
    Parameters
    ----------
    in_df:  pd DataFrame
        input dataframe
    substr: str
        string to filter column
        names by
    Returns
    -------
        list of filtered column names
    """
    return [col for col in in_df if substr in col]

def repl_numeric(sub_df, key_dict):
    """
    Replace strings with numeric score.

    Parameters
    ----------
    sub_df: pd DataFrame
        dataframe containing only cols
        referring to given survey
    key_dict:   dict
        dictionary containing key-value pairs
        for replacement
    rem_newl:   
        whether or not to remove newline characters
        None/not provided = don't strip new lines
        any other value = do remove them.
    
    Returns
    -------
        sub_df, containing numeric representations of
        questionnaire responses.

    """
    sub_df = sub_df.applymap(lambda x: key_dict[x.lower()])
    return sub_df

def strip_unwanted(sub_df,reg_exp):
    """
    Remove unwanted elements from string.

    Parameters
    ----------
    sub_df: pd DataFrame
        dataframe containing questionnaire
        scores in string format
    reg_exp:    str
        this will be the first argument in
        re.sub()
    
    Returns
    -------
        sub_df w/out unwanted content
    """
    sub_df = sub_df.applymap(
                            lambda x: re.sub(reg_exp,
                            "",x).rstrip()
                            )
    return sub_df

def preprocess_subdf(in_df,substr,keys,values,rem_nl = None, strip_re = None):
    """
    Preprocess questionnaire scores.

    Parameters
    ----------
    in_df: pd DataFrame
        main qualtrics dataframe
    substr: str
        substr to identify relevant columns
    keys:   list[str]
        scores as they appear in OG sub_df
    values: list[int]
        numeric scores to replace str vals with
    remove_newlines:
        if provided, remove any unwanted newline
        characters
    strip_re: str, optional
        provide string to use in re.sub(),
        eg for removing brackets from survey
        scores.
    
    Returns
    -------
        sub_df containing numeric rather than str
        scores.
    """
    sub_df = in_df.loc[:, filter_cols(in_df,substr)]
    # remove new line characters if needed
    if rem_nl is not None:
        sub_df = remove_newlines(sub_df,rounds = 2)
    if strip_re is not None:
        sub_df = strip_unwanted(sub_df,strip_re)
    sub_df = repl_numeric(sub_df,make_dict(keys, values))
    return sub_df

def change_header(in_df,col_names,val_range):
    """
    Change head for easier multiplication.

    Parameters
    ----------
    in_df:  pd DataFrame
    col_names:  list[str]
        columns in in_df to rename
    val_range:  array
        range of values ot replace
        string names with
    
    Returns
    -------
    subsection of input dataframe
    with names replaced by values in
    val_range
    """
    sub_df = in_df.loc[:,col_names]
    sub_df.columns = val_range
    return sub_df

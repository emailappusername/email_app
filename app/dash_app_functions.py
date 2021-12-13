# python module to load in some functions that are to be used in the dash app 
import pandas as pd
import json 
import regex as re
# initial function for loading and cleaning data: 

def read_load_clean(data_path): 

    """function designed to do the following: 
    1. Read data in 
    2. Clean date column to be of datetime format 
    3. Sorts values of dataframe by date column
    
    Arguments
    ---------
    data_path -> str 
        - The path to your dataframe 

    Returns 
    ---------
    df -> obj (pandas dataframe)
        - The dataframe with cleaned date and sorted
    
    """
    df = pd.read_pickle(data_path)

    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")

    df.sort_values("date", inplace=True)

    return df 

# function to filter data by date selected: 

def filter_date(dataframe, start_date, end_date): 

    """Filters a dataframe by a start date and end date: 
    1. Takes dataframe 
    2. Filters dateframe based on start and end date 
    3. returns dataframe with new filtered set of data
    
    Arguments
    ---------
    dataframe -> obj 
        - The dataframe you choose 
    start_date -> obj 
        - datetime format object from dash app 
    end_date -> obj 
        - datetime format object from the dash app 
    
    Returns
    -------
    df -> obj (pandas dataframe)
        - The dataframe with filtered date selection
    
    """

    selection = ((dataframe.date >= start_date) & (dataframe.date <= end_date)) 

    df = dataframe.loc[selection,:]

    return df




# new function to obtain the clicked word 

def obtain_clicked_word(event_type= None, radio_button_select = "single_word"):

    """Returns back the clicked word as a regex compiled string 
    
    Arguments
    ---------
    event_type -> Obj
        - An object returned from a clickData event - this is None at runtime 
        - it changes when a user clicks on a bar chart word

    radio_button_select -> str
        - A string of the button selected on the app 
        - when this changes we should set a default being the first word in the data by count - this is based on n-gram dataframes


    Returns 
    --------
    list called clicked_word_output 
    with 
    element 0 as: 
    clicked_word -> Obj 
        - A regex compiled string object to search underlying data to generate plot and datatable at bottom of app
    element 1 as: 
    actual word - > str 
        - the word they have selected used in title of plot only
    s
    """
    # generate empty list
    clicked_word_output = []

    if event_type is None: 

        if radio_button_select == "single_word": 

            clicked_word = "is"

            actual_word = clicked_word # for the title only

        elif radio_button_select == "bi_gram": 

            clicked_word = "hello my"

            actual_word = clicked_word 

        else: 

            clicked_word = "hello my name"

            actual_word = clicked_word
        # clicked_word = re.compile("(?:" + clicked_word + ")")

        # clicked_word_output.append(clicked_word)

        # clicked_word_output.append(actual_word)

    if event_type is not None: 
       
        
        clicked_word = json.dumps(event_type, indent = 2)
        
        clicked_word = json.loads(clicked_word)

        clicked_word = clicked_word['points'][0]['label']

        actual_word = clicked_word # for the title only 

        
    #create the outputs based on the clicked word or default word 
    # if nothing has been selected at all yet! 

    clicked_word = re.compile("(" + clicked_word + ")")

    clicked_word_output.append(clicked_word)

    clicked_word_output.append(actual_word)


    return clicked_word_output   
   


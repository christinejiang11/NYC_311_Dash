import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from fuzzywuzzy import process, fuzz
import pygsheets
from datetime import datetime, date, time, timedelta
import json
warnings.simplefilter("ignore")
pd.options.display.max_columns=50

def preprocess(df):
    df['created_mdy'] = pd.to_datetime(df['created_date'].dt.date)
    df['created_weekday'] = df['created_date'].dt.day_name()
    df['created_week'] = df['created_date'].dt.week
    df['created_hour'] = df['created_date'].dt.hour
    df['hour'] = df['created_date'].dt.strftime('%I %p')
    df['week_start'] = [x-timedelta(days=x.weekday()) for x in df['created_mdy']]
    df['count'] = 1

    #have to convert to categorical so that fuzzy match doesn't take forever
    #these get converted back to strings in order to plot
    df['agency_name'] = df['agency_name'].astype('category')
    df['complaint_type'] = df['complaint_type'].astype('category')
    df['descriptor'] = df['descriptor'].astype('category')
    df['location_type'] = df['location_type'].astype('category')
    df['city'] = df['city'].astype('category')
    df['borough'] = df['borough'].str.capitalize()
    #can't covert NAN to int, so convert to string
    df['incident_zip'] = df['incident_zip'].astype(str).str[0:5]
    df['borough'] = df['borough'].replace('Staten island', 'Staten_Island')
    return df

nyc_311_calls = preprocess(orig_df)

def export_col_values(workbook, df, columns):
    """For a list of columns, creates a new sheet for each column in the Google Sheets workbook and exports each column's unique values and their corresponding value counts to that sheet.
    Users can then use these value counts to determine the final clean categories for each column."""
    for col in columns:
        value_counts = df[col].value_counts()
        counts_df = pd.DataFrame(value_counts).reset_index()
        #cast any categorical columns to strings
        counts_df['index'] = counts_df['index'].astype(str)
        #if the worksheet doesn't already exist for that column, add one
        try:
            worksheet = workbook.worksheet_by_title(col)
        except Exception:
            #ensure the error is in regards to missing the worksheet
            print(sys.exc_info())
            workbook.add_worksheet(col)
            worksheet = workbook.worksheet_by_title(col)
        worksheet.set_dataframe(counts_df, start='A1')

def get_valid_names(workbook, columns, start='D1'):
    """Extract the valid names manually entered by the user in column D in each sheet of the workbook."""
    valid_names = {}
    for col in columns:
        worksheet = workbook.worksheet_by_title(col)
        valid_matrix = worksheet.get_values(start='D1', end='D100')
        valid_names[col] = [v[0] for v in valid_matrix]
    #return dictionary where keys are column names, and each value is a list of valid 'clean' categories
    return valid_names

def fuzzy_match(value):
    """Returns the best match for each column; fuzzy match score of < 90 will return 'Other'"""
    match = process.extract(query=value, choices=valid_names[col], limit=1)
    if match[0][1] < 90:
        return 'Other'
    else:
        return match[0][0]


# In[11]:


#use pygsheets to connect to data cleaning workbook
client = pygsheets.authorize(service_account_file=path+'client_secret.json')
workbook = client.open('311_data_cleaning')
columns = ['agency_name','complaint_type','descriptor','location_type','city']

#export unique column values and their counts
export_col_values(workbook, nyc_311_calls, columns)

#get dictionary of lists with valid names for each column
#change values in column D of each tab if you wish to change the possible output values
valid_names = get_valid_names(workbook, columns, start='D1')

#fuzzy match each of the columns to the available values; create new 'cleaned' column
for col in columns:
    nyc_311_calls['cleaned_'+col] = nyc_311_calls[col].apply(fuzzy_match)

print('Cleaned columns created.')

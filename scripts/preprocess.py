import pandas as pd
import json
from sodapy import Socrata
import pygsheets
from datetime import datetime, date, time, timedelta
from fuzzywuzzy import process, fuzz

path = '../data/'
client = pygsheets.authorize(service_account_file=path+'client_secret.json')
workbook = client.open('311_data_cleaning')

def get_data(chunk_size=100000, begin_date='2020-01-01'):
    #define parameters for endpoint, dataset, and app token
    path ='../data/'
    data_url = 'data.cityofnewyork.us'
    dataset = 'erm2-nwe9'
    with open(path+'client_secret.json') as f:
        credentials = json.load(f)
    app_token = credentials['app_token']

    #sets up the connection, need application token to override throttling limits
    #username and password only required for creating or modifying data
    client = Socrata(data_url, app_token)
    client.timeout = 6000

    #count number of records in desired dataset
    record_count = client.get(dataset, select='count(*)', where="created_date >='2020-01-01'")
    total_count = record_count[0]['count']
    print(total_count)

    start = 0
    results=[]
    #paginate through dataset in sets of 10000 to get all records since start of 2020
    while True:
        print(f'{start} rows retrieved')
        results.extend(client.get(dataset,select="unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, location_type, incident_zip, borough, address_type, city, status, latitude, longitude, location",
                                  where="created_date >= '2020-02-01'",
                                  limit=chunk_size, offset=start))
        start += chunk_size
        if start > int(total_count):
            break
    return results

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

def export_col_values(df, columns):
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

def get_valid_names(columns, start='D1'):
    """Extract the valid names manually entered by the user in column D in each sheet of the workbook."""
    valid_names = {}
    for col in columns:
        worksheet = workbook.worksheet_by_title(col)
        valid_matrix = worksheet.get_values(start='D1', end='D100')
        valid_names[col] = [v[0] for v in valid_matrix]
    #return dictionary where keys are column names, and each value is a list of valid 'clean' categories
    return valid_names

def fuzzy_match(value, col, valid_names):
    """Returns the best match for each column; fuzzy match score of < 90 will return 'Other'"""
    match = process.extract(query=value, choices=valid_names[col], limit=1)
    if match[0][1] < 90:
        return 'Other'
    else:
        return match[0][0]

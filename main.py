
import pandas as pd
import numpy as np
from sodapy import Socrata
import os
import seaborn as sns
from matplotlib import pyplot as plt
from fuzzywuzzy import process, fuzz
import pygsheets
from datetime import datetime, date, time, timedelta
import json 
import math
import warnings
import math
warnings.simplefilter("ignore")
pd.options.display.max_columns=50

from bokeh.plotting import figure, output_file, output_notebook, show, save, reset_output, gmap
from bokeh.models import (ColumnDataSource, GMapOptions, HoverTool, ColorBar, LinearColorMapper, Panel,
                                            Tabs, CheckboxButtonGroup, CheckboxGroup, RadioButtonGroup, TextInput,
                                                  Slider, DateRangeSlider, NumeralTickFormatter, Dropdown, Div, Select, BasicTicker)
from bokeh.palettes import brewer
from bokeh.transform import factor_cmap, transform, linear_cmap
from bokeh.layouts import column, row, layout, WidgetBox
from bokeh.io import output_file, show, curdoc


#define parameters for endpoint, dataset, and app token
path ='../../data/'

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


def get_data(chunk_size=100000, total_rows=int(total_count)):
    start = 0
    results=[]

    #paginate through dataset in sets of 10000 to get all records since start of 2020
    while True:
        print(f'{start} rows retrieved')
        results.extend(client.get(dataset,select="unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, location_type, incident_zip, borough, address_type, city, status, latitude, longitude, location",
                                  where="created_date >= '2020-02-01'",
                                  limit=chunk_size, offset=start))
        start += chunk_size
        if start > total_rows:
            break
    return results

#only run if getting new data
orig_results = get_data()
orig_df = pd.DataFrame(orig_results)
orig_df.to_csv(path+'311_data.csv', index=False)


path ='../../data/'
orig_df = pd.read_csv(path+'311_data.csv',
                      usecols=['unique_key', 'created_date', 'closed_date', 'agency', 'agency_name',
                            'complaint_type', 'descriptor', 'location_type', 'incident_zip', 'borough',
                            'city', 'status', 'latitude', 'longitude', 'location'],
                      parse_dates=['created_date', 'closed_date'])

print(f'df shape: {orig_df.shape}')
print(f'df size: {orig_df.memory_usage().sum()/1024**2:.2f} MB')

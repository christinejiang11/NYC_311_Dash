import pandas as pd
import numpy as np
import pygsheets
from scripts.preprocess import get_data, preprocess, export_col_values, get_valid_names, fuzzy_match
from scripts.heatmap import heatmap_tab
from scripts.bargraph import bargraph_tab
from scripts.geomap import geomap_tab
from bokeh.models import Tabs
from bokeh.plotting import output_file, show
from bokeh.io import curdoc

################# LOAD NEW DATA ##############################
path = '../data/'
orig_results = get_data()
orig_df = pd.DataFrame(orig_results)
orig_df.to_csv(path+'311_data.csv', index=False)
orig_df = pd.read_csv(path+'311_data.csv',
                      usecols=['unique_key', 'created_date', 'closed_date', 'agency', 'agency_name',
                            'complaint_type', 'descriptor', 'location_type', 'incident_zip', 'borough',
                            'city', 'status', 'latitude', 'longitude', 'location'],
                      parse_dates=['created_date', 'closed_date'])
print(f'dataset shape: {orig_df.shape}')
print(f'dataset size: {orig_df.memory_usage().sum()/1024**2:.2f} MB')

################# PREPROCESS AND CLEAN DATA #######################
#workbook with categorical value mappings can be found here: https://bit.ly/3eSoaHA
nyc_311_calls = preprocess(orig_df)

#export unique column values and their counts
columns = ['agency_name','complaint_type','descriptor','location_type','city']
export_col_values(nyc_311_calls, columns)

#get dictionary of lists with clean names for each column
valid_names = get_valid_names(columns, start='D1')
for col in columns:
    nyc_311_calls['cleaned_'+col] = nyc_311_calls[col].apply(fuzzy_match, col=col, valid_names=valid_names)
print('Cleaned columns created.')

##################### CREATE DASHBOARD #####################################
heatmap_1 = heatmap_tab(nyc_311_calls, 'created_weekday','hour','Calls by Day and Hour',
                           x_ticks=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                           y_ticks=list(nyc_311_calls['hour'].unique())[::-1],
                           x_label='Day of Week',
                           y_label='Time of Day',
                           tab_title='Calls by Day/Hour')

heatmap_2 = heatmap_tab(nyc_311_calls, 'week_start','cleaned_descriptor', 'Calls by Complaint Type',
                               x_label='Week Start',
                               y_label='Complaint',
                               exclude=['Other'],
                               tab_title='Calls by Type')

geomap_1 = geomap_tab(nyc_311_calls)

bargraph_1 = bargraph_tab(nyc_311_calls)

tabs = Tabs(tabs=[geomap_1, bargraph_1, heatmap_1, heatmap_2])
curdoc().theme = 'light_minimal'
curdoc().add_root(tabs)

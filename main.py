import pandas as pd
import numpy as np
from preprocess import get_data
from heatmap import heatmap_tab
from bargraph import bargraph_tab
from geomap import geomap_tab

path = '../data/'
orig_results = get_data()
orig_df = pd.DataFrame(orig_results)
orig_df.to_csv(path+'311_data.csv', index=False)
nyc_311_calls = pd.read_csv(path+'311_data.csv')
#
# heatmap_1 = heatmap_tab(nyc_311_calls, 'created_weekday','hour','Calls by Day and Hour',
#                            x_ticks=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
#                            y_ticks=list(nyc_311_calls['hour'].unique())[::-1],
#                            x_label='Day of Week',
#                            y_label='Time of Day',
#                            tab_title='Calls by Day/Hour')
#
# heatmap_2 = heatmap_tab(nyc_311_calls, 'week_start','cleaned_descriptor', 'Calls by Complaint Type',
#                                x_label='Week Start',
#                                y_label='Complaint',
#                                exclude=['Other'],
#                                tab_title='Calls by Type')
#
# geomap_1 = geomap_tab(nyc_311_calls)
#
# bargraph_1 = bargraph_tab(nyc_311_calls)
#
# linegraph_1 = linegraph_tab(nyc_311_calls, 'created_mdy', 'cleaned_descriptor')
# 
# tabs = Tabs(tabs=[geomap1, bargraph1, heatmap_1, heatmap_2, linegraph_1])
# output_file('dashboard.html')
# show(tabs)
# curdoc().theme = 'light_minimal'
# curdoc().add_root(tabs)

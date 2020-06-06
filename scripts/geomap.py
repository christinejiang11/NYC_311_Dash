import pandas as pd
from datetime import date
import math
import json
from bokeh.plotting import figure, output_file, output_notebook, show, save, reset_output, gmap
from bokeh.models import (ColumnDataSource, GMapOptions, HoverTool, ColorBar, LinearColorMapper, Panel,
                                            Tabs, CheckboxButtonGroup, CheckboxGroup, RadioButtonGroup, TextInput,
                                                  Slider, DateRangeSlider, NumeralTickFormatter, Dropdown, Div, Select, BasicTicker)
from bokeh.palettes import brewer
from bokeh.transform import factor_cmap, transform, linear_cmap
from bokeh.layouts import column, row, layout, WidgetBox
from bokeh.io import output_file, show, curdoc

def geomap_tab(nyc_311_calls):
    #load json file with map style
    #map styles to choose from: girly.txt, outspoken.txt, multibrand.txt
    with open('scripts/multibrand.txt') as json_file:
        map_style_json = json.load(json_file)
    map_style = json.dumps(map_style_json)

    def make_dataset(boroughs, display_num, start_date, end_date):
        #nyc_311_calls['created_mdy'] = pd.to_datetime(nyc_311_calls['created_mdy'])
        date_filter = nyc_311_calls[(nyc_311_calls['created_mdy'] >= start_date) & (nyc_311_calls['created_mdy'] <= end_date)]
        borough_filter = date_filter[date_filter['borough'].isin(boroughs)]
        borough_filter['lat_round'] = round(borough_filter['latitude'],3)
        borough_filter['lon_round'] = round(borough_filter['longitude'],3)
        latlon_df = pd.DataFrame(borough_filter.groupby(['lat_round', 'lon_round'])['count'].sum()).reset_index()
        latlon_df['sizes'] = latlon_df['count']/latlon_df['count'].max()*150
        latlon_sorted = latlon_df.sort_values('sizes', ascending=False)
        latlon_display = latlon_sorted[:display_num]
        return ColumnDataSource(latlon_display)

    def style(p):
        p.title.align = 'center'
        p.title.text_font_size = '19pt'
        p.axis.axis_label_text_font_size = '12pt'
        p.axis.major_label_text_font_size = '10pt'

        p.title.text_font = 'avenir'
        p.axis.axis_label_text_font = 'avenir'
        p.axis.major_label_text_font = 'avenir'

        p.title.text_color = 'dimgray'
        p.axis.major_label_text_color = 'dimgray'
        p.axis.axis_label_text_color = 'dimgray'

        p.xaxis.axis_label = 'Latitude'
        p.yaxis.axis_label = 'Longitude'

        p.title.text_font_style = 'normal'
        p.axis.axis_label_text_font_style = 'normal'
        p.axis.major_label_text_font_style = 'normal'
        return p

    def make_plot(src):
        path = '../data/'
        with open(path+'client_secret.json') as f:
            data = json.load(f)
        api_key = data['google_api_key']
        map_options = GMapOptions(lat=40.76, lng=-73.95, map_type='roadmap', zoom=12, styles=map_style)
        call_map = gmap(api_key, map_options, title='311 Calls by Location', plot_width=850, plot_height=850)
        call_map.circle(x='lon_round', y='lat_round', size='sizes', source=src, fill_alpha=0.8,
                        fill_color='tomato', line_color='firebrick')
        hover = HoverTool(tooltips=[('Longitude','@lon_round{0.0}'),
                                    ('Latitude','@lat_round{0.0}'),
                                    ('Calls','@count{0,0}')])
        call_map.add_tools(hover)
        call_map = style(call_map)
        return call_map

    def update(attr, old, new):
        boroughs_to_plot = [borough_selection.labels[i] for i in borough_selection.active]
        top_n = int(display_labels[display_group.active][4:])
        if isinstance(date_range_slider.value[0], (int, float)):
        # pandas expects nanoseconds since epoch
            start_date = pd.Timestamp(float(date_range_slider.value[0])*1e6)
            end_date = pd.Timestamp(float(date_range_slider.value[1])*1e6)
        else:
            start_date = pd.Timestamp(date_range_slider.value[0])
            end_date = pd.Timestamp(date_range_slider.value[1])
        new_src = make_dataset(boroughs_to_plot, top_n, start_date, end_date)
        src.data.update(new_src.data)

    #set boroughs available for selection
    available_boroughs = list(set(nyc_311_calls['borough']))
    available_boroughs.sort()

    #checkbox for neighborhoods
    borough_selection = CheckboxGroup(labels=available_boroughs, active=[0,1,2,3,4])
    borough_selection.on_change('active', update)

    #radio button for top N records to display
    display_labels = ['Top 5', 'Top 100', 'Top 1000', 'Top 5000']
    display_group = RadioButtonGroup(labels=display_labels, active=3)
    display_group.on_change('active', update)

    #slider for date range
    date_range_slider = DateRangeSlider(title="Date Range", start=date(2020, 1, 1), end=date.today(), value=(date(2020, 1, 1), date.today()),
                                        step=1, bar_color='goldenrod', tooltips=True)
    date_range_slider.on_change('value', update)

    div1 = Div(text="""Records to Display:""", width=200, height=15)
    div2 = Div(text="""Boroughs:""", width=200, height=15)

    #set initial dataset params
    initial_boroughs = [borough_selection.labels[i] for i in borough_selection.active]
    start_date = pd.to_datetime(date_range_slider.value[0])
    end_date = pd.to_datetime(date_range_slider.value[1])
    top_n = int(display_labels[display_group.active][4:])

    #create initial plot
    src = make_dataset(initial_boroughs, top_n, start_date, end_date)
    p = make_plot(src)
    controls = WidgetBox(date_range_slider, div1, display_group, div2, borough_selection)
    layout = row(controls, p)
    tab = Panel(child=layout, title='Calls by Location')
    return tab

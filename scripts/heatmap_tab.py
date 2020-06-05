import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta

from bokeh.plotting import figure, output_file, output_notebook, show, save, reset_output, gmap
from bokeh.models import (ColumnDataSource, GMapOptions, HoverTool, ColorBar, LinearColorMapper, Panel,
                                            Tabs, CheckboxButtonGroup, CheckboxGroup, RadioButtonGroup, TextInput,
                                                  Slider, DateRangeSlider, NumeralTickFormatter, Dropdown, Div, Select, BasicTicker)
from bokeh.palettes import brewer
from bokeh.transform import factor_cmap, transform, linear_cmap
from bokeh.layouts import column, row, layout, WidgetBox
from bokeh.io import output_file, show, curdoc

def heatmap_tab(nyc_311_calls, x, y, title=None, x_ticks=None, y_ticks=None, x_label=None, y_label=None, exclude=None, tab_title='Heatmap'):

    #dataset for heatmap given x-category, y-category, boroughs, start date, and end date
    #user can indicate a value to exclude in either the x-category or y-category
    def make_dataset(x, y, boroughs, start_date, end_date):
        date_filter = nyc_311_calls[(nyc_311_calls['created_mdy'] >= start_date) & (nyc_311_calls['created_mdy'] <= end_date)]
        borough_filter = date_filter[date_filter['borough'].isin(boroughs)]
        pivot = borough_filter.pivot_table(values='count', index=x, columns=y, aggfunc='sum')
        pivot.columns = pivot.columns.astype(str)
        pivot.index = pivot.index.astype(str)
        if exclude:
            for exclusion in exclude:
                try:
                    pivot = pivot.drop(exclusion)
                except KeyError:
                    pivot = pivot.drop(exclusion, axis=1)
                except:
                    print('Exclusion does not exist in index or columns.')
        df_pivot = pd.DataFrame(pivot.stack()).reset_index()
        df_pivot.columns = ['x','y','value']
        return ColumnDataSource(df_pivot)

    def style(p):
        p.title.align = 'center'
        p.grid.visible=False
        p.title.text_font_size = '19pt'
        p.axis.axis_label_text_font_size = '12pt'
        p.axis.major_label_text_font_size = '10pt'

        p.title.text_font = 'avenir'
        p.axis.axis_label_text_font = 'avenir'
        p.axis.major_label_text_font = 'avenir'

        p.title.text_color = 'dimgray'
        p.axis.major_label_text_color = 'dimgray'
        p.axis.axis_label_text_color = 'dimgray'

        p.xaxis.axis_label = x_label
        p.yaxis.axis_label = y_label
        p.xaxis.major_label_orientation = math.pi/4

        p.title.text_font_style = 'normal'
        p.axis.axis_label_text_font_style = 'normal'
        p.axis.major_label_text_font_style = 'normal'
        p.xaxis.major_label_orientation = 'vertical'
        return p

    def make_plot(src):
        colors = ["#4f685f",'#64827c',"#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#f9eed4", "#f9d1ac", "#ddb7b1", "#cc7878", "#a54c4c","#933b41", "#550b1d"]
        mapper = LinearColorMapper(palette='Magma256', low=src.data['value'].min(), high=src.data['value'].max())

        #user can indicate specific order for x or y ticks
        if x_ticks:
            x_range = x_ticks
        else:
            x_range = sorted(list(set(src.data['x'])))

        if y_ticks:
            y_range = y_ticks
        else:
            y_range = sorted(list(set(src.data['y'])))

        p = figure(plot_width=1100, plot_height=700, x_range=x_range, y_range=y_range, title=title)
        p.rect(x='x', y='y', width=1, height=1, source=src, line_color='white', fill_color=transform('value', mapper), fill_alpha=0.7)
        color_bar = ColorBar(color_mapper=mapper, location=(0,0), ticker=BasicTicker(desired_num_ticks=len(colors)), scale_alpha=0.7)
        p.add_layout(color_bar, 'right')
        hover = HoverTool(tooltips=[(y,'@y'), (x,'@x'), ('Calls','@value{0,0}')])
        p.add_tools(hover)
        p = style(p)
        return p

    def update(attr, old, new):
        boroughs_to_plot = [borough_selection.labels[i] for i in borough_selection.active]
        if isinstance(date_range_slider.value[0], (int, float)):
            start_date = pd.Timestamp(float(date_range_slider.value[0])*1e6)
            end_date = pd.Timestamp(float(date_range_slider.value[1])*1e6)
        else:
            start_date = pd.Timestamp(date_range_slider.value[0])
            end_date = pd.Timestamp(date_range_slider.value[1])
        new_src = make_dataset(x, y, boroughs_to_plot, start_date, end_date)
        src.data.update(new_src.data)
        print('plotting new stuff')
        p.rect(x='x', y='y', width=1, height=1, source=src, line_color='white', fill_color=transform('value', mapper))
        color_bar = ColorBar(color_mapper=mapper, location=(0,0), ticker=BasicTicker(desired_num_ticks=len(colors)))
        p.add_layout(color_bar, 'right')
        print('new stuff done')

    #set boroughs available for selection
    available_boroughs = list(set(nyc_311_calls['borough']))
    available_boroughs.sort()

    #checkbox for neighborhoods
    borough_selection = CheckboxGroup(labels=available_boroughs, active=[0,1,2,3,4,5])
    borough_selection.on_change('active', update)

    #date range selection
    date_range_slider = DateRangeSlider(title="Date Range: ", start=date(2020, 1, 1), end=date.today(), value=(date(2020, 1, 1), date.today()),
                                        step=1, bar_color='#a5bab7', tooltips=True)
    date_range_slider.on_change('value',update)

    #set initial params
    initial_boroughs = [borough_selection.labels[i] for i in borough_selection.active]
    start_date = pd.to_datetime(date_range_slider.value[0])
    end_date = pd.to_datetime(date_range_slider.value[1])

    #create initial plot
    src = make_dataset(x, y, initial_boroughs, start_date, end_date)
    plot = make_plot(src)
    controls = WidgetBox(date_range_slider, borough_selection)
    layout = row(controls, plot)
    tab = Panel(child=layout, title=tab_title)
    return tab

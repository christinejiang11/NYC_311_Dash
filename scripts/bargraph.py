import pandas as pd
from datetime import date
import math
from bokeh.plotting import figure, output_file, output_notebook, show, save, reset_output, gmap
from bokeh.models import (ColumnDataSource, GMapOptions, HoverTool, ColorBar, LinearColorMapper, Panel,
                                            Tabs, CheckboxButtonGroup, CheckboxGroup, RadioButtonGroup, TextInput,
                                                  Slider, DateRangeSlider, NumeralTickFormatter, Dropdown, Div, Select, BasicTicker)
from bokeh.palettes import brewer
from bokeh.transform import factor_cmap, transform, linear_cmap
from bokeh.layouts import column, row, layout, WidgetBox
from bokeh.io import output_file, show, curdoc

def bargraph_tab(nyc_311_calls):
    #dataset for bar graph given boroughs, categorical variable, start date, and end date
    #only top 15 records are shown
    def make_dataset(boroughs, category, start_date, end_date):
        date_filter = nyc_311_calls[(nyc_311_calls['created_mdy'] >= start_date) & (nyc_311_calls['created_mdy'] <= end_date)]
        borough_filter = date_filter[date_filter['borough'].isin(boroughs)]
        df = pd.DataFrame(borough_filter.groupby([category, 'borough'])['count'].sum()).reset_index()
        df_pivot = df.pivot_table(values='count', index=category, columns='borough')
        df_pivot['sum'] = df_pivot.sum(axis=1)
        df_sorted = df_pivot.sort_values('sum', ascending=False).fillna(0)[:15]
        return ColumnDataSource(df_sorted)

    def style(p):
        p.title.align = 'center'
        p.title.text_font_size = '19pt'
        p.axis.axis_label_text_font_size = '12pt'
        p.axis.major_label_text_font_size = '10pt'

        p.title.text_font = 'avenir'
        p.axis.axis_label_text_font = 'avenir'
        p.axis.major_label_text_font = 'avenir'
        p.legend.label_text_font = 'avenir'

        p.title.text_color = 'dimgray'
        p.axis.major_label_text_color = 'dimgray'
        p.axis.axis_label_text_color = 'dimgray'
        p.xaxis.axis_label = 'Calls'

        p.title.text_font_style = 'normal'
        p.axis.axis_label_text_font_style = 'normal'
        p.axis.major_label_text_font_style = 'normal'
        p.legend.label_text_font_style = 'normal'

        p.toolbar_location = None
        p.xaxis.formatter=NumeralTickFormatter(format="0,0")
        p.legend.location = "bottom_right"
        return p

    #horizontal stacked bar graph: y-axis is unique category values, bars are split by boroughs
    def make_plot(src, title):
        active_category_values = list(reversed(src.data[active_category]))
        boroughs = [x for x in list(src.data.keys()) if x in available_boroughs]
        colors=brewer['YlGnBu'][len(boroughs)]
        p = figure(y_range=active_category_values, title=title, plot_height=700, plot_width=1100)
        p.hbar_stack(boroughs, y=active_category, height=0.9, source=src, color=colors, legend=[x.lower() for x in boroughs], fill_alpha=0.8)
        category_value = f'@{active_category}'
        #format number values in hover tool annotations as '10,000'
        hover = HoverTool(tooltips=[(display_category, category_value),
                                    ('Brooklyn', '@Brooklyn{0,0}'),
                                    ('Bronx','@Bronx{0,0}'),
                                    ('Staten Island', '@Staten_Island{0,0}'),
                                    ('Manhattan', '@Manhattan{0,0}'),
                                    ('Queens', '@Queens{0,0}'),
                                    ('Unspecified','@Unspecified{0,0}')])
        p.add_tools(hover)
        p = style(p)
        return p

    def update(attr, old, new):
        #set new categorical variable, boroughs, and colors to plot
        category_to_plot = labels_lookup[category_select.value]
        boroughs_to_plot = [borough_selection.labels[i] for i in borough_selection.active]
        colors=brewer['BuPu'][len(boroughs_to_plot)]
        #convert date range slider values to timestamp, given dtype of returned value
        if isinstance(date_range_slider.value[0], (int, float)):
            start_date = pd.Timestamp(float(date_range_slider.value[0])*1e6)
            end_date = pd.Timestamp(float(date_range_slider.value[1])*1e6)
        else:
            start_date = pd.Timestamp(date_range_slider.value[0])
            end_date = pd.Timestamp(date_range_slider.value[1])
        new_src = make_dataset(boroughs_to_plot, category_to_plot, start_date, end_date)
        src.data.update(new_src.data)

        #this isn't working - trying to plot new y axis and x axis label given values chosen
        category_to_plot_values = list(src.data[category_to_plot])
        p = figure(y_range=category_to_plot_values, title=category_to_plot, plot_height=700, plot_width=1100)
        p.hbar_stack(boroughs_to_plot, y=category_to_plot, height=0.9, source=src, color=colors, legend=[x.lower() for x in boroughs_to_plot])
        p.xaxis.axis_label = category_to_plot
        p.title.text = display_category
        print(f'new category: {category_to_plot}, new boroughs: {boroughs_to_plot}, start: {start_date}, end: {end_date}')

    #set boroughs available for selection
    available_boroughs = list(set(nyc_311_calls['borough']))
    available_boroughs.sort()

    #checkbox for boroughs
    borough_selection = CheckboxGroup(labels=available_boroughs, active=[0,1,2,3,4,5])
    borough_selection.on_change('active', update)

    #slider for date range
    date_range_slider = DateRangeSlider(title="Date Range: ", start=date(2020, 1, 1), end=date.today(), value=(date(2020, 1, 1), date.today()),
                                        step=10, bar_color='#8c96c6', tooltips=True)
    date_range_slider.on_change('value', update)

    #dropdown for which category to plot
    display_labels = ['Agency', 'City', 'Descriptor', 'Location Type', 'Status', 'Zip Code']
    actual_labels = ['agency_name', 'cleaned_city', 'cleaned_descriptor', 'cleaned_location_type', 'status', 'incident_zip']
    labels_lookup = {display:actual for display, actual in zip(display_labels, actual_labels)}
    category_select = Select(title="Category:", value='Agency', options=display_labels)
    category_select.on_change('value', update)

    #divider text for borough checkbox
    div = Div(text="""Borough:""", width=200, height=15)

    #set initial dataset params
    display_category = category_select.value
    active_category = labels_lookup[display_category]
    initial_boroughs = [borough_selection.labels[i] for i in borough_selection.active]
    start_date = pd.to_datetime(date_range_slider.value[0])
    end_date = pd.to_datetime(date_range_slider.value[1])

    #create initial plot
    src = make_dataset(initial_boroughs, active_category, start_date, end_date)
    p = make_plot(src, f'Calls by {display_category}')
    controls = WidgetBox(date_range_slider, category_select, div, borough_selection)
    layout = row(controls, p)
    tab = Panel(child=layout, title='Calls by Category')
    tabs = Tabs(tabs=[tab])
    return tab

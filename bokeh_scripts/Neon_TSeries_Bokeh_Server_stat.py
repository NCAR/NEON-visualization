#! /usr/bin/env python
## TODO: clean up imports
#Import Libraries
##%matplotlib inline

import os
import sys
import glob
import argparse
import requests
import time

import numpy as np
import pandas as pd
import xarray as xr
import yaml 

#import plotly.graph_objects as go

from os.path import join, expanduser
from glob import glob

import matplotlib
import matplotlib.pyplot as plt
from scipy import stats



#time-series with Dropdown menu for values

#import yaml
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Slider , Dropdown, Select, PreText, Label, Slope, Band
from bokeh.layouts import row,column
# make a simple plot time-series

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

def mae(predict, actual):
    """
    Examples(rounded for precision):
    >>> actual = [1,2,3];predict = [1,4,3]
    >>> np.around(mae(predict,actual),decimals = 2)
    0.67
    >>> actual = [1,1,1];predict = [1,1,1]
    >>> mae(predict,actual)
    0.0
    """
    predict = np.array(predict)
    actual = np.array(actual)

    difference = abs(predict - actual)
    score = difference.mean()

    return score

def mbd(predict, actual):
    """
    This value is Negative, if the model underpredicts,
    positive, if it overpredicts.
    Example(rounded for precision):
    Here the model overpredicts
    >>> actual = [1,2,3];predict = [2,3,4]
    >>> np.around(mbd(predict,actual),decimals = 2)
    50.0
    Here the model underpredicts
    >>> actual = [1,2,3];predict = [0,1,1]
    >>> np.around(mbd(predict,actual),decimals = 2)
    -66.67
    """

    difference = predict - actual
    numerator = np.sum(difference) / len(predict)
    denumerator = np.sum(actual) / len(predict)
    # print(numerator, denumerator)
    score = float(numerator) / denumerator * 100

    return score


def in_notebook():
    from IPython import get_ipython
    if get_ipython():
        return True
    else:
        return False  

ShowWebpage = True

if in_notebook():
    ShowWebpage = False

if ShowWebpage:
    pass
else:
    output_notebook()
    
    

    
    
    
neon_sites = ["ABBY", "BART", "BLAN", 
              "CPER", "DCFS", "DSNY",
              "GRSM", "HARV", "JERC",
              "KONZ", "MOAB", 
              "NOGP", "OAES", "ORNL",
              "OSBS", "SERC",
              "SOAP", "SRER", "STEI",
              "TALL", "TREE", "UKFS", "UNDE", "WOOD"]


print ('Total number of NEON sites for this demo:', len(neon_sites))


def get_neon_pkl_files(pkl_dir, neon_site, years):
    pkl_names = []
    for year in years:
        pkl_names.extend(glob(join(pkl_dir, neon_site+'_'+year+'df_all.pkl')))
    return pkl_names


years =['2018','2019','2020']

df_list =[]

for neon_site in neon_sites:

    pkl_dir = '../sample_data/processed_data'
    pkl_names = get_neon_pkl_files(pkl_dir, neon_site, years)
    print (pkl_names)

    for pkl_name in pkl_names:
        processed_data = os.path.join(pkl_name)
        df_all = pd.read_pickle(processed_data).reset_index()
        df_all['site']=neon_site
        df_list.append(df_all)
    
df_all_sites = pd.concat(df_list)


df_all = df_all_sites


#-- extract year, month, day, hour information from time
df_all['year'] = df_all['time'].dt.year
df_all['month'] = df_all['time'].dt.month
df_all['day'] = df_all['time'].dt.day
df_all['hour'] = df_all['time'].dt.hour

df_all['ELAI'] = np.nan

df_all ['NEE'] = df_all['NEE']*60*60*24
df_all ['sim_NEE'] = df_all['sim_NEE']*60*60*24
df_all ['GPP'] = df_all['GPP']*60*60*24

df_all ['sim_GPP'] = df_all['sim_GPP']*60*60*24

freq_list = ['all','hourly','daily','monthly']


def get_data (df_all, var, freq, this_site):
    print ('this_site', this_site)
    df=df_all[df_all['site']==this_site]
    sim_var_name = "sim_"+var
    #print (df['site'])
    if freq=="monthly":
        df = df.groupby(['year','month']).mean().reset_index()
        df["day"]=15
        df['time']=pd.to_datetime(df[["year", "month","day"]])
        #if var=='NEE' or var=='GPP':
        #    df

    elif freq=="daily":
        #print (df)

        df = df.groupby(['year','month','day']).mean().reset_index()
        df['time']=pd.to_datetime(df[["year", "month", "day"]])

    elif freq=="hourly":
        df = df.groupby(['year','month','day','hour']).mean().reset_index()
        df['time']=pd.to_datetime(df[["year", "month", "day","hour"]])
    
    elif freq=="all":
        df = df
    
    df_new = pd.DataFrame({'time':df['time'],'NEON':df[var],'CLM':df[sim_var_name]})
    
    #print(df_new)
    return df_new

def find_regline(df, var, sim_var_name):
        # find the trendline:
        #sim_var_name = "sim_"+var
        #print (var)
        #print (sim_var_name)

        df_temp = df[[var, sim_var_name]]#.dropna()
        
        #df_temp = pd.DataFrame(df, columns)
        df_temp.dropna(inplace=True)
        #print (df_temp)

        #z = np.polyfit(df_temp[var], df_temp[sim_var_name], 1)
        #p = np.poly1d(z)
        
        #-----
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_temp[var], df_temp[sim_var_name])
        return slope, intercept, r_value, p_value, std_err
    
    
    
plot_vars =['FSH','EFLX_LH_TOT','Rnet','NEE','GPP','ELAI']


def simple_tseries(doc):
    #-- default values:
    
    default_site = 'ABBY'
    default_freq = 'daily'
    defualt_var = 'EFLX_LH_TOT'
    default_var_desc = "Latent Heat Flux [W/m2]"
    
    df_new = get_data(df_all, defualt_var,default_freq,default_site)
    source = ColumnDataSource(df_new)

    #-- what are tools options
    #tools = "pan, wheel_zoom, box_zoom ,box_select,lasso_select, undo, redo, save, reset, hover, crosshair, tap"
    #tools = "tap"
    
    p_tools = "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, hover, crosshair"
    q_tools = "pan,  box_zoom, box_select, lasso_select, undo, redo, reset, crosshair"

    def tseries_plot(p):
        p.line('time', 'NEON', source=source, alpha=0.8, line_width=4, color="navy", legend_label="NEON")
        p.line('time', 'CLM',source=source , alpha=0.8, line_width=3, color="red", legend_label="CLM")
        p.circle('time', 'NEON', size=2, source=source, color=None, selection_color="navy")
        p.circle('time', 'CLM', size=2, source=source, color=None, selection_color="red")
        
        #p.circle('time', 'var', source=source, alpha=0.8, color="navy")

        p.xaxis.major_label_text_color = 'dimgray'
        p.xaxis.major_label_text_font_size = '18px'
        p.xaxis.major_label_text_font_style = "bold"

        p.yaxis.major_label_text_color = 'dimgray'
        p.yaxis.major_label_text_font_size = '18px'
        p.yaxis.major_label_text_font_style = "bold"


        p.xaxis.axis_label_text_font_size = "15pt"
        p.xaxis.axis_label_text_font_style = "bold"
        
        p.yaxis.axis_label_text_font_size = "15pt"
        p.yaxis.axis_label_text_font_style = "bold"
        
        p.axis.axis_label_text_font_style = "bold"
        
        p.grid.grid_line_alpha = 0.5
        p.title.text_font_size = '18pt'
        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = 'Latent Heat Flux [W/m2]'

        p.title.text = "Time-Series Plot for Neon Site : " +default_site
        
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "13pt"
        p.legend.label_text_font_style = "bold"

        #p.legend.label_text_font = "times"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.25

    def scatter_plot(q):
        #q.circle('NEON', 'CLM', source=source, alpha=0.8, color="navy",fill_alpha=0.2, size=10, hover_color = "firebrick")
        q.circle('NEON', 'CLM', source=source, alpha=0.8, color="navy",fill_alpha=0.2, size=10, hover_color = "firebrick", selection_color="orange", nonselection_alpha=0.1, selection_alpha=0.5)
        q.xaxis.major_label_text_color = 'dimgray'
        q.xaxis.major_label_text_font_size = '15px'
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = 'dimgray'
        q.yaxis.major_label_text_font_size = '15px'
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "13pt"
        q.yaxis.axis_label_text_font_size = "13pt"

        q.axis.axis_label_text_font_style = "bold"
        q.grid.grid_line_alpha = 0.5
        q.title.text_font_size = '15pt'
        q.xaxis.axis_label = 'NEON'
        q.yaxis.axis_label = 'CLM'
        
        #q.xaxis.major_label_orientation = "vertical"
        q.xaxis.major_label_orientation = np.pi/4
        
        #x = range(0,500)
        #y = range(0,500)

        #q.line(x, y,alpha=0.8, line_width=4, color="gray")
    
        
    p = figure(tools=p_tools, x_axis_type="datetime", title= "Neon Time-Series "+neon_site)
    tseries_plot(p)   
    
    q_width = 550
    q_height = 550
    q = figure(tools=q_tools,width=350, height=350, x_range=p.y_range, y_range=p.y_range)
    #q = figure(tools=q_tools,width=350, height=350)
    scatter_plot(q)
    
    q.add_tools(
        HoverTool(
            tooltips=[
                      ("NEON", "$x"),
                      ("CLM", "$y")]
        )
    )
    
    
    #q.add_tools(
    #    HoverTool(tooltips=[('date', '@tooltip')],
    #      formatters={'@DateTime': 'datetime'})
    #)
    
    stats = PreText(text='', width=500)

    menu = Select(options=plot_vars,value=defualt_var, title='Variable') 
    menu_freq = Select(options=freq_list,value=default_freq, title='Frequency') 
    menu_site = Select(options=neon_sites,value=default_site, title='Neon Site') 

    def update_variable (attr, old, new):
        print ('updating plot for:')
        print (' - var  : ', menu.value)
        print (' - freq : ', menu_freq.value)
        print (' - site : ', menu_site.value)
        
        df_new = get_data(df_all, menu.value, menu_freq.value, menu_site.value)

        #q.add_layout(mytext)
        #q.add_layout(regression_line)
        
        #source = ColumnDataSource(df_new)
        source.data =df_new
        #source.stream(df_new)


    def update_site (attr, old, new):
        
        df_new = get_data(df_all, menu.value, menu_freq.value, menu_site.value)
        source.data.update =df_new
        #source.stream(df_new)
        #print (menu.value)
        #print (menu_freq.value)
        print (menu_site.value)
        p.title.text = "Time-Series Plot for Neon Site : " +menu_site.value

    def update_yaxis (attr, old, new):
        if (menu.value=='EFLX_LH_TOT'):
            p.yaxis.axis_label = 'Latent Heat Flux [W/m2]'
        elif (menu.value=='FSH'):
            p.yaxis.axis_label = 'Sensible Heat Flux [W/m2]'
        elif (menu.value=='Rnet'):
            p.yaxis.axis_label = 'Net Radiation [W/m2]'
        elif (menu.value=='NEE'):
            p.yaxis.axis_label = 'Net Ecosystem Exchange [gC/m2day]'
        elif (menu.value=='GPP'):
            p.yaxis.axis_label = 'Gross Primary Production [gC/m2day]'
        elif (menu.value=='ELAI'):
            p.yaxis.axis_label = 'Exposed Leaf Area Index'


    menu.on_change('value', update_variable)
    menu.on_change('value', update_yaxis)

    menu_freq.on_change('value', update_variable)
    
    menu_site.on_change('value', update_variable)
    menu_site.on_change('value', update_site)
    
    
    #layout = row(column(menu, menu_freq, menu_site, q),  p)
    layout = row(p, column( menu, menu_freq, menu_site, q))
    #layout = gridplot([[p, q]])

    doc.add_root(layout)
    
    doc.theme = Theme(json=yaml.load("""
        attrs:
            Figure:
                background_fill_color: "#FFFFFF"
                outline_line_color: grey
                toolbar_location: above
                height: 550
                width: 1100
            Grid:
                grid_line_dash: [6, 4]
                grid_line_color: grey
    """, Loader=yaml.FullLoader))


def simple_tseries_sync_stat(doc):
    default_site = 'ABBY'
    default_freq = 'daily'
    defualt_var = 'EFLX_LH_TOT'
    default_var_desc = "Latent Heat Flux [W/m2]"
    df_new = get_data(df_all, defualt_var,default_freq,default_site)
    source = ColumnDataSource(df_new)

    #-- what are tools options
    #tools = "pan, wheel_zoom, box_zoom ,box_select,lasso_select, undo, redo, save, reset, hover, crosshair, tap"
    #tools = "tap"
    
    p_tools = "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, hover, crosshair"
    q_tools = "pan,  box_zoom, box_select, lasso_select, undo, redo, reset, crosshair"

    def tseries_plot(p):
        p.line('time', 'NEON', source=source, alpha=0.8, line_width=4, color="navy", legend_label="NEON")
        p.line('time', 'CLM',source=source , alpha=0.8, line_width=3, color="red", legend_label="CLM")
        p.circle('time', 'NEON', size=2, source=source, color=None, selection_color="navy")
        p.circle('time', 'CLM', size=2, source=source, color=None, selection_color="red")

        #p.circle('time', 'var', source=source, alpha=0.8, color="navy")

        p.xaxis.major_label_text_color = 'dimgray'
        p.xaxis.major_label_text_font_size = '18px'
        p.xaxis.major_label_text_font_style = "bold"

        p.yaxis.major_label_text_color = 'dimgray'
        p.yaxis.major_label_text_font_size = '18px'
        p.yaxis.major_label_text_font_style = "bold"


        p.xaxis.axis_label_text_font_size = "15pt"
        p.xaxis.axis_label_text_font_style = "bold"
        
        p.yaxis.axis_label_text_font_size = "15pt"
        p.yaxis.axis_label_text_font_style = "bold"
        
        p.axis.axis_label_text_font_style = "bold"
        
        p.grid.grid_line_alpha = 0.5
        p.title.text_font_size = '18pt'
        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = 'Latent Heat Flux [W/m2]'

        p.title.text = "Time-Series Plot for Neon Site : " +default_site
        
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "13pt"
        p.legend.label_text_font_style = "bold"

        #p.legend.label_text_font = "times"
        p.legend.label_text_color = "dimgray"
        p.legend.background_fill_alpha = 0.25

    def scatter_plot(q):
        q.circle('NEON', 'CLM', source=source, alpha=0.8, color="navy",fill_alpha=0.2, size=10, hover_color = "firebrick", selection_color="orange", nonselection_alpha=0.1, selection_alpha=0.5)

        q.xaxis.major_label_text_color = 'dimgray'
        q.xaxis.major_label_text_font_size = '15px'
        q.xaxis.major_label_text_font_style = "bold"

        q.yaxis.major_label_text_color = 'dimgray'
        q.yaxis.major_label_text_font_size = '15px'
        q.yaxis.major_label_text_font_style = "bold"

        q.xaxis.axis_label_text_font_size = "13pt"
        q.yaxis.axis_label_text_font_size = "13pt"

        q.axis.axis_label_text_font_style = "bold"
        q.grid.grid_line_alpha = 0.5
        q.title.text_font_size = '15pt'
        q.xaxis.axis_label = 'NEON'
        q.yaxis.axis_label = 'CLM'
        
        #q.xaxis.major_label_orientation = "vertical"
        q.xaxis.major_label_orientation = np.pi/4
        #q.title.text = slope_label
        #q.title.text = str(rmse(df_new['CLM'], df_new['NEON']))
        #x = range(0,500)
        #y = range(0,500)

        #q.line(x, y,alpha=0.8, line_width=4, color="gray")
    
        
    p = figure(tools=p_tools, x_axis_type="datetime", title= "Neon Time-Series "+neon_site)
    tseries_plot(p)

    q_width = 550
    q_height = 550
    q = figure(tools=q_tools,width=350, height=350, x_range=p.y_range, y_range=p.y_range)
    #q = figure(tools=q_tools,width=350, height=350)
    scatter_plot(q)
    
    q.add_tools(
        HoverTool(
            tooltips=[
                      ("NEON", "$x"),
                      ("CLM", "$y")]
        )
    )
    
    
    #q.add_tools(
    #    HoverTool(tooltips=[('date', '@tooltip')],
    #      formatters={'@DateTime': 'datetime'})
    #)
    
    stats = PreText(text='', width=500, style={'font-size':'15pt', 
                     'color': 'grey', 
                     'font-weight': 'bold',
                     'font-family': 'Arial'})

    menu = Select(options=plot_vars,value=defualt_var, title='Variable') 
    menu_freq = Select(options=freq_list,value=default_freq, title='Frequency') 
    menu_site = Select(options=neon_sites,value=default_site, title='Neon Site') 
    
    def update_stats(df_new):
        rmse_text = 'RMSE : ' +str(rmse(df_new['CLM'], df_new['NEON']))
        mae_text = 'MAE  : ' +str(mae(df_new['CLM'], df_new['NEON']))
        mbd_text = 'MBD  : ' +str(mbd(df_new['CLM'], df_new['NEON']))
        line =  "---------------------------- "
        stats.text = str(df_new[['NEON','CLM']].describe()) +'\n' + line + '\n'+rmse_text +'\n'+mae_text+'\n'+mbd_text
        
    def update_variable (attr, old, new):
        print ('updating plot for:')
        print (' - var  : ', menu.value)
        print (' - freq : ', menu_freq.value)
        print (' - site : ', menu_site.value)
        
        df_new = get_data(df_all, menu.value, menu_freq.value, menu_site.value)
        update_stats(df_new)

        #q.add_layout(mytext)
        #q.add_layout(regression_line)
        
        #source = ColumnDataSource(df_new)
        source.data =df_new
        #source.stream(df_new)


    def update_site (attr, old, new):
        
        df_new = get_data(df_all, menu.value, menu_freq.value, menu_site.value)
        source.data.update =df_new
        #source.stream(df_new)
        #print (menu.value)
        #print (menu_freq.value)
        print (menu_site.value)
        p.title.text = "Time-Series Plot for Neon Site : " +menu_site.value

    def update_yaxis (attr, old, new):
        if (menu.value=='EFLX_LH_TOT'):
            p.yaxis.axis_label = 'Latent Heat Flux [W/m2]'
        elif (menu.value=='FSH'):
            p.yaxis.axis_label = 'Sensible Heat Flux [W/m2]'
        elif (menu.value=='Rnet'):
            p.yaxis.axis_label = 'Net Radiation [W/m2]'
        elif (menu.value=='NEE'):
            p.yaxis.axis_label = 'Net Ecosystem Exchange [gC/m2day]'
        elif (menu.value=='GPP'):
            p.yaxis.axis_label = 'Gross Primary Production [gC/m2day]'
        elif (menu.value=='ELAI'):
            p.yaxis.axis_label = 'Exposed Leaf Area Index'



    menu.on_change('value', update_variable)
    menu.on_change('value', update_yaxis)

    menu_freq.on_change('value', update_variable)
    
    menu_site.on_change('value', update_variable)
    menu_site.on_change('value', update_site)
            
    def selection_change(attrname, old, new):
        print ("calling dsjkghkjasdhgkjads")
        df_new = get_data(df_all, menu.value, menu_freq.value, menu_site.value)
        selected = source.selected.indices
        if selected:
            df_new = df_new.iloc[selected, :]
        update_stats(df_new)
        
    source.selected.on_change('indices', selection_change)
    
    #layout = row(column(menu, menu_freq, menu_site, q),  p)
    layout = column(row(p, column( menu, menu_freq, menu_site, q)), stats)
    #layout = gridplot([[p, q]])

    doc.add_root(layout)
    
    doc.theme = Theme(json=yaml.load("""
        attrs:
            Figure:
                background_fill_color: "#FFFFFF"
                outline_line_color: grey
                toolbar_location: above
                height: 550
                width: 1100
            Grid:
                grid_line_dash: [6, 4]
                grid_line_color: grey
    """, Loader=yaml.FullLoader))

    #select_overlay = q.select_one(BoxSelectTool).overlay
    #select_overlay.fill_color = "firebrick"
    #select_overlay.line_color = None
    #source.selected.on_change('indices', callback1)
    #source.on_change('selected', callback1)



    



from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool

#output_notebook()

if ShowWebpage:
    simple_tseries_sync_stat(curdoc())
else:
    #show(bkapp)
    show(simple_tseries_sync_stat)

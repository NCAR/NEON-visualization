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



valid_vars = ['TBOT','FSDS','NEE','FSH','EFLX_LH_TOT','GPP']
neon_sites = ["NIWO","ABBY", "HARV"]
neon_site = "HARV"


processed_data = "../notebooks/df_all.pkl"

df_all = pd.read_pickle(processed_data).reset_index()

df_all.head()


df_all['season'] = ((df_all['month']%12+3)//3).map({1:'DJF', 2: 'MAM', 3:'JJA', 4:'SON'})

def get_diel_df (df, var, season):
    
    if (season != "Annual"):
        df = df[df['season']==season]
    
    diel_df_mean = df.groupby('hour').mean().reset_index()
    diel_df_std = df.groupby('hour').std().reset_index()

    sim_var_name = "sim_"+var
    bias_var_name = "bias_"+var
    std_var_name = "std_"+var
    
    diel_df_mean[bias_var_name] = diel_df_mean[sim_var_name]-diel_df_mean[var]
    
    df_new = pd.DataFrame({'hour':diel_df_mean['hour'],'NEON':diel_df_mean[var],'CLM':diel_df_mean[sim_var_name]})
    
   # df_new ['CLM'][-1] = diel_df_mean[sim_var_name][0]
    
    print (df_new['CLM'])
    df_new['Bias'] = diel_df_mean[sim_var_name] - diel_df_mean[var]
    df_new['NEON_lower'] = diel_df_mean[var]-diel_df_std[var]
    df_new['NEON_upper'] = diel_df_mean[var]+diel_df_std[var]

    df_new['CLM_lower'] = diel_df_mean[sim_var_name]-diel_df_std[sim_var_name]
    df_new['CLM_upper'] = diel_df_mean[sim_var_name]+diel_df_std[sim_var_name]

    return df_new

def find_regline(df, var, sim_var_name):

        df_temp = df[[var, sim_var_name]]
        #df_temp = pd.DataFrame(df, columns)
        df_temp.dropna(inplace=True)
        #print (df_temp)

        #z = np.polyfit(df_temp[var], df_temp[sim_var_name], 1)
        #p = np.poly1d(z)
        
        #-----
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_temp[var], df_temp[sim_var_name])
        return slope, intercept, r_value, p_value, std_err
    



                        
def diel_doc(doc):
    
    
    df_new = get_diel_df(df_all, 'TBOT','DJF')
    print (df_new)
    
    source = ColumnDataSource(df_new)

    #-- what are tools options
    tools = "hover, box_zoom, undo, crosshair"
    p = figure(tools=tools, title= "Neon Diel Cycle "+neon_site)

    def diel_shaded_plot(p):
        p.line('hour', 'NEON', source=source, alpha=0.8, line_width=4, color="navy", legend_label="NEON")
        p.line('hour', 'CLM',source=source , alpha=0.8, line_width=3, color="red", legend_label="CLM")

        p.line('hour', 'NEON_lower',source=source , alpha=0.5, line_width=3, color="#6495ED")
        p.line('hour', 'NEON_upper',source=source , alpha=0.5, line_width=3, color="#6495ED")

        band_neon = Band(base='hour', lower='NEON_lower', upper='NEON_upper', source=source,level='underlay',
                fill_alpha=0.3,fill_color='#6495ED')
    
        band_clm = Band(base='hour', lower='CLM_lower', upper='CLM_upper', source=source,level='underlay',
                fill_alpha=0.3,fill_color='#F08080')
    
        p.line('hour', 'CLM_lower',source=source , alpha=0.5, line_width=3, color="#F08080")
        p.line('hour', 'CLM_upper',source=source , alpha=0.5, line_width=3, color="#F08080")
    
        p.add_layout(band_neon)
        p.add_layout(band_clm)

        p.xaxis.major_label_text_color = 'dimgray'
        p.xaxis.major_label_text_font_size = '15px'
        p.yaxis.major_label_text_color = 'dimgray'
        p.yaxis.major_label_text_font_size = '15px'
    
        p.xaxis.axis_label_text_font_size = "0pt"
        p.axis.axis_label_text_font_style = "bold"
        p.grid.grid_line_alpha = 0.5
        p.title.text_font_size = '15pt'
    
    diel_shaded_plot(p)

    
    
    q_width = 950
    q_height = 270
    q = figure(tools=tools,width=q_width, height=q_height)
    

    
    q.line('hour', 'Bias', source=source, alpha=0.8, line_width=4, color="green", legend_label="Bias")

    q.xaxis.major_label_text_color = 'dimgray'
    q.xaxis.major_label_text_font_size = '15px'
    q.yaxis.major_label_text_color = 'dimgray'
    q.yaxis.major_label_text_font_size = '15px'
    
    q.xaxis.axis_label_text_font_size = "15pt"
    q.yaxis.axis_label_text_font_size = "13pt"

    q.axis.axis_label_text_font_style = "bold"
    q.grid.grid_line_alpha = 0.5
    q.title.text_font_size = '15pt'
    q.xaxis.axis_label = 'Hour'
    #q.yaxis.axis_label = 'CLM'

    p.add_tools(
    HoverTool(
        tooltips=[('value','@value{2.2f}'), 
                      ('index', '@index')]
        )
    )

        
    zeros = np.zeros(26)

    
    x= range(-1,25)
    print (len(x))
    print (zeros.size)
    q.line (x, zeros,line_width=4, color="darkgray", alpha=0.8,line_dash="dashed")

    
    
    def scatter_plot(q):
        q.circle('NEON', 'CLM', source=source, alpha=0.8, color="navy",fill_alpha=0.2, size=10)

        q.xaxis.major_label_text_color = 'dimgray'
        q.xaxis.major_label_text_font_size = '15px'
        q.yaxis.major_label_text_color = 'dimgray'
        q.yaxis.major_label_text_font_size = '15px'
    
        q.xaxis.axis_label_text_font_size = "13pt"
        q.yaxis.axis_label_text_font_size = "13pt"

        q.axis.axis_label_text_font_style = "bold"
        q.grid.grid_line_alpha = 0.5
        q.title.text_font_size = '15pt'
        q.xaxis.axis_label = 'NEON'
        q.yaxis.axis_label = 'CLM'
        
        slope, intercept, r_value, p_value, std_err = find_regline(df_new, 'NEON','CLM')
        print ("new r_value:",r_value)
        slope_label = "y="+"{:.2f}".format(slope)+"+"+"{:.2f}".format(intercept)+"x"+" (R2="+"{:.2f}".format(r_value)+")"
        mytext = Label(text=slope_label , x=0+20, y=q_height-100, 
                        x_units="screen", y_units='screen', text_align="left")
        
        regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")
        
        print (mytext)
        #q.add_layout(mytext)
        q.add_layout(regression_line)
        q.title.text = slope_label
        
        #x = range(0,500)
        #y = range(0,500)

        #q.line(x, y,alpha=0.8, line_width=4, color="gray")
    
    q_width = 350
    q_height = 350
    qq = figure(tools=tools,width=350, height=350)
    scatter_plot(qq)

    
    


    


    def update_site (attr, old, new):
        p.title.text = "Neon Diurnal Cycle " +menu_site.value

    def update_stats(df_new):
        stats.text = str(df_new[['NEON','CLM']].describe())

    def update_variable (attr, old, new):
        
        print (menu.value)
        df_new = get_diel_df(df_all, menu.value, menu_season.value)
        update_stats(df_new)

        source.data =df_new
        #diel_shaded_plot(p)
        #scatter_plot(qq)
        #scatter_plot(q)
        #source.stream(df_new)
        
        slope, intercept, r_value, p_value, std_err = find_regline(df_new, 'NEON','CLM')
        #print (r_value)
        slope_label = "y="+"{:.2f}".format(slope)+"+"+"{:.2f}".format(intercept)+"x"+" (R2="+"{:.2f}".format(r_value)+")"
        #mytext = Label(text=slope_label , x=0+20, y=q_height-100, 
        #                x_units="screen", y_units='screen', text_align="left")
        
        #regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")

        #q.add_layout(mytext)
        #print (q)
        qq.title.text = slope_label
        #q.add_layout(regression_line)
        

    menu = Select(options=valid_vars,value='TBOT', title='Variable') 
    menu_season =  Select(options=["DJF","MAM", "JJA", "SON", "Annual"],value='DJF', title='Season') 
    
    stats = PreText(text='Statistical Summary:', width=250)
        
        
    menu.on_change('value', update_variable)
    menu_season.on_change('value', update_variable)



    menu_site = Select(options=neon_sites,value='HARV', title='Neon Site') 
    menu_site.on_change('value', update_site)

    
    #layout = row(column(menu, menu_freq, menu_site, q),  p)
    layout = row(column(p,q), column( menu, menu_season, menu_site, stats,qq))
    doc.add_root(layout)
    
    doc.theme = Theme(json=yaml.load("""
        attrs:
            Figure:
                background_fill_color: "#FFFFFF"
                outline_line_color: white
                toolbar_location: above
                height: 450
                width: 950
            Grid:
                grid_line_dash: [6, 4]
                grid_line_color: gray
    """, Loader=yaml.FullLoader))
    

from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool

#output_notebook()

if ShowWebpage:
    diel_doc(curdoc())
else:
    #show(bkapp)
    show(diel_doc)




from glob import glob
from os.path import join, expanduser
import time
import xarray as xr
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import requests
import pandas as pd
import os
import matplotlib.colors as colors
import tqdm

#time-series with Dropdown menu for values
from scipy import stats

import yaml
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Slider , Dropdown, Select, PreText, Label, Slope
from bokeh.layouts import row,column
# make a simple plot time-series

from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
#from neon_bokeh_utils import simple_tseries

import os
os.environ['BOKEH_RESOURCES'] = 'inline'

from bokeh.resources import INLINE
import bokeh.io
from bokeh import *
bokeh.io.output_notebook(INLINE)


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
        
    #elif freq=="weekly":
    #    df = df.apply(lambda x: x.resample('7D', on='date').mean().reset_index())    
        
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
    

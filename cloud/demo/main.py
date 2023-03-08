#! /usr/bin/env python

import numpy as np
import pandas as pd
import xarray as xr
import yaml 

from scipy import stats

from tqdm import tqdm
import fsspec
import ujson

import warnings

import gcsfs
from google.cloud import storage

from bokeh.models import Button, DatetimeTickFormatter

from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Select, PreText, DatePicker
from bokeh.layouts import row,column
from bokeh.models import HoverTool
from bokeh.plotting import figure, show

from glob import glob

warnings.simplefilter("ignore") 

nchunks = 200

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
    
    
neon_sites = ["ABBY", "BARR", "BART", "BLAN", "BONA",
              "CLBJ", "CPER", "DCFS", "DEJU", "DELA", "DSNY",
              "GRSM", "GUAN", "HARV", "HEAL", "JERC", "JORN",
              "KONA", "KONZ", "LAJA", "LENO", "MLBS", "MOAB", 
              "NOGP", "OAES", "ONAQ", "ORNL",
              "OSBS", "RMNP", "SCBI", "SERC", "SJER",
              "SOAP", "SRER", "STEI", "STER",
              "TALL", "TEAK", "TOOL", "TREE", "UKFS", "UNDE", "WOOD", "WREF", "YELL"]


print ('Total number of NEON sites for this demo:', len(neon_sites))

df_list =[]

freq_list = ['all','hourly','daily','monthly']


def get_data (var, freq, this_site, date, clmchunks, neonchunks):

    month = date[0:7]

    gcs_file_system = gcsfs.GCSFileSystem()
    client = storage.Client()

    # get CLM data
    json_list = client.list_blobs('neon-ncar-dev', prefix='jsons-gcs-monthly/'+this_site+".transient.clm2.h1."+month)
    m_list = []
    for js in tqdm(json_list):
       with gcs_file_system.open("gs://neon-ncar-dev/" + js.name) as f:
        m_list.append(fsspec.get_mapper("reference://", fo=ujson.load(f)))
    ds_clm = xr.open_mfdataset(m_list, combine='by_coords', engine='zarr', coords='minimal', data_vars='minimal', compat='override', decode_times=True, parallel=True, chunks={"time": clmchunks})

    # get NEON data
    json_list = client.list_blobs('neon-ncar-dev', prefix='jsons-gcs-monthly/'+this_site+"_eval_"+month)
    m_list = []
    for js in tqdm(json_list):
      with gcs_file_system.open("gs://neon-ncar-dev/" + js.name) as f:
        m_list.append(fsspec.get_mapper("reference://", fo=ujson.load(f)))
    ds_neon = xr.open_mfdataset(m_list, combine='by_coords', engine='zarr', decode_times=True, chunks={"time": neonchunks})   

    # convert values
    if (var == 'EFLX_LH_TOT'):
        neon_data = np.ravel(ds_neon[var])
        clm_data = np.ravel(ds_clm['FCEV'] + ds_clm['FCTR'] + ds_clm['FGEV'])
    elif (var == 'Rnet'):
        neon_data = np.ravel(ds_neon[var])
        clm_data = np.ravel(ds_clm['FSA'] - ds_clm['FIRA'])
    elif (var == 'NEE'):
        neon_data = np.ravel(ds_neon[var])
        clm_data = -np.ravel(ds_clm['GPP'] - ds_clm['AR'] + ds_clm['HR'])
    elif (var == 'ELAI'):
        neon_data = np.nan
        clm_data = np.ravel(ds_clm[var])
    elif (var == 'GPP'):
        neon_data = np.ravel(ds_neon[var])
        clm_data = np.ravel(ds_clm[var]*60*60*24)
    else:
        neon_data = np.ravel(ds_neon[var])
        clm_data = np.ravel(ds_clm[var])

    df_new = pd.DataFrame({'time':ds_clm['time'],'NEON':neon_data,'CLM':clm_data})

    df_new['year'] = df_new['time'].dt.year
    df_new['month'] = df_new['time'].dt.month
    df_new['day'] = df_new['time'].dt.day
    df_new['hour'] = df_new['time'].dt.hour

    if freq=="monthly":
        df_new = df_new.groupby(['year','month']).mean().reset_index()
        df_new["day"]=15
        df_new['time']=pd.to_datetime(df_new[["year", "month","day"]])
    elif freq=="daily":
        df_new = df_new.groupby(['year','month','day']).mean().reset_index()
        df_new['time']=pd.to_datetime(df_new[["year", "month", "day"]])
    elif freq=="hourly":
        df_new = df_new.groupby(['year','month','day','hour']).mean().reset_index()
        df_new['time']=pd.to_datetime(df_new[["year", "month", "day","hour"]])

    return df_new

def find_regline(df, var, sim_var_name):

        df_temp = df[[var, sim_var_name]]

        df_temp.dropna(inplace=True)

        slope, intercept, r_value, p_value, std_err = stats.linregress(df_temp[var], df_temp[sim_var_name])
        return slope, intercept, r_value, p_value, std_err
    
    
    
plot_vars =['FSH','EFLX_LH_TOT','Rnet','NEE','GPP','ELAI']


def simple_tseries_sync_stat(doc):

    default_site = 'ABBY'
    default_freq = 'hourly'
    default_var = 'EFLX_LH_TOT'
    default_date = '2018-12-01'
    default_var_desc = "Latent Heat Flux [W/m2]"
    df_new = get_data(default_var,default_freq,default_site, default_date, nchunks, nchunks)

    source = ColumnDataSource(df_new)
    
    p_tools = "pan, wheel_zoom, box_zoom, box_select, undo, redo, save, reset, hover, crosshair"
    q_tools = "pan,  box_zoom, box_select, lasso_select, undo, redo, reset, crosshair"

    def tseries_plot(p):
        p.line('time', 'NEON', source=source, alpha=0.8, line_width=4, color="navy", legend_label="NEON")
        p.line('time', 'CLM',source=source , alpha=0.8, line_width=3, color="red", legend_label="CLM")
        p.circle('time', 'NEON', size=2, source=source, color=None, selection_color="navy")
        p.circle('time', 'CLM', size=2, source=source, color=None, selection_color="red")

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

        p.xaxis[0].formatter = DatetimeTickFormatter(days=["%Y-%m-%d"])

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
        
        q.xaxis.major_label_orientation = np.pi/4
    
    neon_site='ABBY'
    p = figure(tools=p_tools, x_axis_type="datetime", title= "Neon Time-Series "+neon_site)
    tseries_plot(p)

    q_width = 550
    q_height = 550
    q = figure(tools=q_tools,width=350, height=350, x_range=p.y_range, y_range=p.y_range)

    scatter_plot(q)
    
    q.add_tools(
        HoverTool(
            tooltips=[
                      ("NEON", "$x"),
                      ("CLM", "$y")]
        )
    )
    
    stats = PreText(text='', width=500, style={'font-size':'15pt', 
                     'color': 'grey', 
                     'font-weight': 'bold',
                     'font-family': 'Arial'})

    menu = Select(options=plot_vars,value=default_var, title='Variable') 
    menu_freq = Select(options=freq_list,value=default_freq, title='Frequency') 
    menu_site = Select(options=neon_sites,value=default_site, title='Neon Site') 
    date_picker = DatePicker(title='Select date', value=default_date, min_date="2018-01-01", max_date="2022-02-28")
    button = Button(label='Update')
    
    def update_stats(df_new):
        rmse_text = 'RMSE : ' +str(rmse(df_new['CLM'], df_new['NEON']))
        mae_text = 'MAE  : ' +str(mae(df_new['CLM'], df_new['NEON']))
        mbd_text = 'MBD  : ' +str(mbd(df_new['CLM'], df_new['NEON']))
        line =  "---------------------------- "
        stats.text = str(df_new[['NEON','CLM']].describe()) +'\n' + line + '\n'+rmse_text +'\n'+mae_text+'\n'+mbd_text
        

    def load_data():

        df_new = get_data(menu.value, menu_freq.value, menu_site.value, date_picker.value, nchunks, nchunks)
        update_stats(df_new)
        source.data =df_new
        p.title.text = "Time-Series Plot for Neon Site : " +menu_site.value
        update_yaxis()
        button.label = "Update"


    def update_data():

        button.label = "Loading..."
        curdoc().add_next_tick_callback(load_data)


    def update_date (attr, old, new):
        
        date_picker.value = date_picker.value[0:7] + "-01"


    def update_yaxis ():
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

            
    date_picker.on_change('value', update_date)

    button.on_click(update_data)

    def selection_change(attrname, old, new):
        print ("calling dsjkghkjasdhgkjads")
        df_new = get_data(menu.value, menu_freq.value, menu_site.value, date_picker.value, nchunks, nchunks)
        selected = source.selected.indices
        if selected:
            df_new = df_new.iloc[selected, :]
        update_stats(df_new)
        
    def spinner_url():
        spinner = self.spinner
        if callable(spinner):
            return spinner(self.color)  # pylint: disable=not-callable
        return spinner

    source.selected.on_change('indices', selection_change)
    
    layout = column(row(p, column( menu, menu_freq, menu_site, date_picker, button, q)), stats)
    curdoc().add_root(column(layout))
    
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


from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, DatePicker

if ShowWebpage:
    simple_tseries_sync_stat(curdoc())
else:
    show(simple_tseries_sync_stat)

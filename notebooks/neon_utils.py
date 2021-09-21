from glob import glob
from os.path import join, expanduser
import time
import xarray as xr

import matplotlib
import matplotlib.pyplot as plt




def preprocess (ds):
    variables = [
        'TSOI',
        'H2OSOI'
    ]


    ds_new= ds[variables]
    return ds_new

def quick_soil_profile(sim_path, case_name, var, year):
    
    plt.rcParams["font.weight"] = "bold"    
    plt.rcParams["axes.labelweight"] = "bold"
    font = {'weight' : 'bold',
                'size'   : 15} 
    matplotlib.rc('font', **font)
    
    sim_files = sorted(glob(join(sim_path,case_name+".h1."+year.__str__()+"*.nc")))
    print("All Simulation files: [", len(sim_files), "files]")
    
    start = time.time()
    ds_ctsm = xr.open_mfdataset(sim_files, decode_times=True, preprocess=preprocess, combine='by_coords',parallel=True)
    end = time.time()
    
    print("Reading all simulation files [", len(sim_files), "files] took:", end-start, "s.")
        
    if var=='TSOI':
        ds_ctsm[var].isel(levgrnd=(slice(0,9))).plot(x="time",yincrease=False, robust=True,cmap='YlOrRd',figsize=(15, 5))
    elif var=='H2OSOI':
        ds_ctsm[var].isel(levsoi=(slice(0,14))).plot(x="time",yincrease=False, robust=True,cmap='BrBG',figsize=(15, 5))
    else:
        print ('Please choose either TSOI or H2SOI for plotting.')
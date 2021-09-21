from glob import glob
from os.path import join, expanduser
import time
import xarray as xr

import matplotlib
import matplotlib.pyplot as plt
import requests
import pandas as pd
import os


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
        
        
        
        
def list_neon_eval_files(neon_site):                               
    """              
    A function to download and parse neon listing file.
    """
    # -- download listing.csv
    listing_file = 'listing.csv'
    url = 'https://neon-ncar.s3.data.neonscience.org/listing.csv'
    download_file(url, listing_file)
                     
    df = pd.read_csv(listing_file)
    df = df[df['object'].str.contains(neon_site+"_eval")]
    
    #df=df.join(df['object'].str.split("/", expand=True))
    dict_out = dict(zip(df['object'],df['last_modified']))
    #df_out = df[['object','6','last_modified']]
    #print (df['last_modified'])
    #print (df_out)  
    #print (df['last_modified'].to_datetime())
    return dict_out  
                     
                     
def download_file(url, fname):
    """              
    Function to download a file.
    Args:            
        url (str):   
            url of the file for downloading
        fname (str) : 
            file name to save the downloaded file.
    """              
    response = requests.get(url)
                     
    with open(fname, 'wb') as f:
        f.write(response.content)
                     
    #-- Check if download status_code
    if response.status_code == 200:
        print('Download finished successfully for', fname,'.')
    elif response.status_code == 404:
        print('File '+fname+'was not available on the neon server:'+ url) 
        
        
def download_eval_files (neon_site, eval_dir):
    file_time = list_neon_eval_files(neon_site)
    site_eval_dir = os.path.join(eval_dir,neon_site)
    if not os.path.isdir(site_eval_dir):
        os.mkdir(site_eval_dir)
    
    for key, value in file_time.items():
        print (key)
        fname = os.path.join(site_eval_dir, key.rsplit('/',1)[1])
        print (fname)
        download_file(key, fname)
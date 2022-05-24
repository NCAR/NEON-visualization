# NEON-visualization
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NCAR/NEON-visualization.git/main)

[![Docker Pulls](https://img.shields.io/docker/pulls/escomp/ctsm-lab-2.3-preview)](https://hub.docker.com/r/escomp/ctsm-lab-2.3-preview)

Repository to include all neon-related visualization scripts. 

--------------
To install all required libraries:
```
conda env create --name neon -f environment.yml
conda activate neon
```
--------------
``bokeh_script`` folder:  
Includes the stand-alone script for running the diurnal cycle outside the notebook: to show case stand-alone application. 
![image](https://user-images.githubusercontent.com/17344536/128048052-b31c3d8c-1f0d-4148-aef1-fd64b04d8526.png)

First, load your environment. 
Next, run the following:
```
python -m bokeh serve  --show ./02-Neon_Evaluation_diel_cycle_dev.py  --port 5012
```

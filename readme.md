# Dashboard Salzach & Saalach Hydrology

[![latest](https://img.shields.io/github/last-commit/iiasa/CWatM_salzburg_dash)](https://github.com/iiasa/CWatM_salzburg_dash)
[![license](https://img.shields.io/github/license/iiasa/CWatM_salzburg_dash?color=1)](https://github.com/iiasa/CWatM_salzburg_dash/blob/main/LICENSE)
[![size](https://img.shields.io/github/repo-size/iiasa/CWatM_salzburg_dash)](https://github.com/iiasa/CWatM_salzburg_dash)

## https://waterstressatpinzgau.herokuapp.com

## Overview 

Dashboard Salzburg & Salzach show the future hydrology of the Salzach and Saalach rivers.   

This tool is under discussion with the authorities of the Land Salzburg, but is in no means official

or has any connections with the land Salzburg. It is a draft tooll of the project Waterstress AT


It is using the climate proejections from ZAMG (OEKS15) to project the hydrological regime for every 1x1 km2 cell in the study area

The hydrology is calculated with the oper-source hydrological model CWatM  https://cwatm.iiasa.ac.at/

## Project

The dashboard is related to the project

**Climate change induced waterstress: challenges and opportunities in Austrian regions (WaterStressAT)**

https://iiasa.ac.at/projects/WaterStressAT

With the Partners:

- International Institute for Applied Systems Analysis (IIASA)
- Environment Agency Austria
- Central Institute for Meteorology and Geodynamics (ZAMG)
- University of Graz

## Publication

- Guillaumot, L., Smilovic, M., Burek, P., de Bruijn, J., Greve, P., Kahil, T., and Wada, Y.: Coupling a large-scale hydrological model (CWatM) with a high-resolution groundwater flow model to assess the impact of irrigation at regional scale, Geosci. Model Dev. Discuss. [preprint], https://doi.org/10.5194/gmd-2022-161, in review, 2022
- Burek, P., Satoh, Y., Kahil, T., Tang, T., Greve, P., Smilovic, M., Guillaumot, L., Zhao, F., and Wada, Y.: Development of the Community Water Model (CWatM v1.04) - a high-resolution hydrological model for global and regional assessment of integrated water resources management, Geosci. Model Dev., 13, 3267–3298, https://doi.org/10.5194/gmd-13-3267-2020, 2020.


## Requirements

The dashboard is using Python 3.8, + libraries (see requirements.txt)
It is created uisng plotly for the figures, dash for the webinterface at at the moment Heroku for web deployment

https://dash.plotly.com/deployment

https://dashboard.heroku.com/apps/waterstressatpinzgau


## Deploy with Heroku

### Initialization of a virtuel envirionment

(Done only once at the beginning)

- cd P:\watmodel\dashboards\waterstressat_pinzgau
- git init        # initializes an empty git repo
- virtualenv venv
- .\venv\Scripts\activate
- pip list

### Instalation of libraries 

(also only once)

- pip install plotly
- pip install gunicorn
- pip install netCDF4
- pip install xarray
- pip install numpy
- pip install pandas  
- pip install dash
- pip install dash-bootstrap-components

To create new requirement.txt:

- pip freeze > requirements.txt

**All the libraries in your app.py**

In the directory should be:
- app.py
- .gitignore
- Procfile
- requirements.txt

## Warm start

- cd P:\watmodel\dashboards\waterstressat_pinzgau
- virtualenv venv

## Test app.py

P:/watmodel/dashboards/waterstressat_pinzgau/venv/Scripts/python app.py 

## First time deploy to heroku 

- heroku login 
- heroku create waterstressatpinzgau  # change my-dash-app to a unique name -> only small letters no underscore
- git add . # add all files to git
- git commit -m 'Initial app water1'
- git push heroku master # deploy code to heroku
- heroku ps:scale web=1  # run the app with a 1 heroku "dyno"

You should be able to view your app at https://waterstressatpinzgau.herokuapp.com 

if errors:

- heroku logs --tail
- heroku logs > log1.txt


## Update the code and redeploy

When you modify app.py with your own code, you will need to add the changes to git and push those changes to heroku.

- heroku login
- change Tourtoise-git/ settings / remote -> https://git.heroku.com/waterstressatpinzgau.git

Update git and deploy

- git status 
- git add . 
- git commit -m "a description of the changes"
- git push heroku master

https://waterstressatpinzgau.herokuapp.com





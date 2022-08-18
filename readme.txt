readme
======
PB

https://dash.plotly.com/deployment
https://dashboard.heroku.com/apps/globalwaterbalance/deploy/heroku-git

# --------------------
cd P:\watmodel\dashboards\waterstressat_pinzgau

$ git init        # initializes an empty git repo
$ .\venv\Scripts\activate

$.\venv\Scripts\activate
$pip list
$ pip install dash
$ pip install plotly
$ pip install gunicorn
$ pip install netCDF4
$ pip install xarray
$pip install numpy
$pip install pandas  
pip install dash-bootstrap-components

-> all the libraries in your app.py
In the directory should be:
app.py
.gitignore
Procfile
requirements.txt
To create new requirement.txt:
$pip freeze > requirements.txt

# -------- test app.py
$python app.py 
P:\watmodel\dashboards\waterstressat_pinzgau\venv\Scripts/python app.py 

    
$ heroku create waterstressatpinzgau
# change my-dash-app to a unique name -> only small letters no underscore

$ git add . # add all files to git
$ git commit -m 'Initial app water1'
$ git push heroku master # deploy code to heroku
$ heroku ps:scale web=1  # run the app with a 1 heroku "dyno"

You should be able to view your app at https://my-dash-app.herokuapp.com (changing my-dash-app to the name of your app).

#----------------------------------------------------
if errors:
heroku logs --tail
heroku logs > log1.txt



#----------------------------------------------------
5. Update the code and redeploy

When you modify app.py with your own code, you will need to add the changes to git and push those changes to heroku.
- Any ms-dos box
- change to cd C:\work\waterbalance\global_json\salzburg
- heroku login
- change Tourtoise-git/ settings / remote -> https://git.heroku.com/waterstressatpinzgau.git


$ git status 
$ git add . 
$ git commit -m "a description of the changes"
$ git push heroku master

https://waterstressatpinzgau.herokuapp.com/

# ----------------------------------------------




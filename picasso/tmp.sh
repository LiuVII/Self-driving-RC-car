virtualenv env --python=python3
source env/bin/activate
export FLASK_APP=picasso
export PICASSO_SETTINGS=/Users/robotics/Desktop/sdc/picasso/config.py 
flask run

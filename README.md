to run the flask app first:
$ export FLASK_APP=app.py

then to run type:
$ flask run


to enter debug mode:
$ export FLASK_ENV=development
$ flask run


Postgress app
$ export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"

adding new models to the database:
$ python 
>>> from app import db
>>> db.create_all()
>>> exit()
import os
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
# Connect to the database
SQLALCHEMY_TRACK_MODIFICATIONS = False
#db connection
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:azoozyh1122@localhost:5432/project'

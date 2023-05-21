import os
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
#db connection - insted of.. SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:azoozyh1122@localhost:5432/project'
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'azoozyh1122')
DB_NAME = os.getenv('DB_NAME', 'project')
DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
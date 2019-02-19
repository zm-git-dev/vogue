"""DEBUG = True

SECRET_KEY = 'MySuperSecretKey'

DB_URI =  "mongodb://localhost:27017"
DB_NAME = 'trending'"""

# encoding: utf-8
import os

# mongo
DB_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['MONGO_DBNAME']
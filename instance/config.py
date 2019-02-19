# encoding: utf-8
import os

# mongo
DB_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['MONGO_DBNAME']

DEBUG = True
SECRET_KEY = 'MySuperSecretKey'
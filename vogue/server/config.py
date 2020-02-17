# encoding: utf-8
import os

# mongo
DB_URI = os.environ['VOGUE_MONGO_URI']
DB_NAME = os.environ['VOGUE_MONGO_DBNAME']

DEBUG = os.environ['VOGUE_FLASK_DEBUG']
SECRET_KEY = os.environ['VOGUE_SECRET_KEY']

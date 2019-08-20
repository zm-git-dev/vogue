# encoding: utf-8
import os

# mongo
DB_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['MONGO_DBNAME']

DEBUG = os.environ['FLASK_DEBUG']
SECRET_KEY = os.environ['VOGUE_SECRET_KEY']


SQLALCHEMY_DATABASE_URI='mysql+pymysql://remoteuser:lq33sym@localhost:3308/genotype'

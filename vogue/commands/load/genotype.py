from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Column, Integer, String, DateTime, Text, Enum,ForeignKey, UniqueConstraint, Numeric, Date)
from sqlalchemy.orm import relationship, backref


SQLALCHEMY_DATABASE_URI='mysql+pymysql://remoteuser:lq33sym@localhost:3308/genotype'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

class Sample(db.Model):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    status = Column(String(255))
    sex = Column(String(255))
    created_at = Column(DateTime)

class Plate(db.Model):
    __tablename__ = 'plate'
    plate_id = Column(Integer, primary_key=True)

class Genotype(db.Model):
    __tablename__ = 'genotype'
    id = Column(Integer, primary_key=True)
    rsnumber = Column(String(255))
    allele_1 = Column(String(255))
    allele_2 = Column(String(255))
    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    analysis = relationship('Analysis', backref = backref('genotype'))

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('sample.id'))
    sample = relationship('Sample', backref = backref('analysis'))
    plate_id = Column(Integer, ForeignKey('plate.plate_id'))
    plate = relationship('Plate', backref = backref('analysis'))
    type = Column(String(255))
    sex = Column(String(255))
    created_at = Column(DateTime)


import datetime


def build_genotypes(analysis_id):
    genotype_dict = {}
    genotypes = Genotype.query.filter(Genotype.analysis_id == analysis_id).all()
    for genotype in genotypes:
        genotype_dict[genotype.rsnumber] = [genotype.allele_1, genotype.allele_2]
    return genotype_dict

def compare(analysis_1, analysis_2):
    snps = analysis_1.keys()
    compare_dict = {}
    for snp in snps:
        if analysis_1[snp] == analysis_2[snp]:
            compare_dict[snp] = True
        else:
            compare_dict[snp] = False
    return compare_dict

def build_sample(sample):
    analysis = Analysis.query.filter(Analysis.sample_id == sample.id).all()
    mongo_sample = {
                'status' : sample.status,
                'date' : sample.created_at,
                'sex' : sample.sex}
    snps = {}
    for ana in analysis:
        if ana.plate:
            mongo_sample['plate']= ana.plate
        snps[ana.type] = build_genotypes(ana.id)
        if snps.get('sequence') and snps.get('genotype'):
            snps['comp'] = compare(snps['sequence'], snps['genotype'])

    mongo_sample['snps'] = snps
    return mongo_sample

def load_one(sample_id):
    sample = Sample.query.filter(Sample.id == sample_id).first()
    mongo_sample = build_sample(sample)
    print(mongo_sample)


def load_many():
    current_time = datetime.datetime.utcnow()
    three_days_ago = current_time - datetime.timedelta(days=120)
    samples = Sample.query.filter(Sample.created_at > three_days_ago).all()
    for sample in samples:
        mongo_sample = build_sample(sample)
        print(mongo_sample)


from sqlalchemy import (Column, Integer, String, DateTime, Text, Enum,ForeignKey, UniqueConstraint, Numeric, Date)
from sqlalchemy.orm import relationship, backref

from vogue.server.auto import app
db = app.genotype_db

class Sample(db.Model):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    status = Column(String(255))
    sex = Column(String(255))
    created_at = Column(DateTime)

class Plate(db.Model):
    __tablename__ = 'plate'
    plate_id = Column(String(255), primary_key=True)

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
    plate_id = Column(String(255), ForeignKey('plate.plate_id'))
    plate = relationship('Plate', backref = backref('analysis'))
    type = Column(String(255))
    sex = Column(String(255))
    created_at = Column(DateTime)



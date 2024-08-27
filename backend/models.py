from pydantic import BaseModel
from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    scores = relationship('TeamScore', back_populates='team')

class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    scores = relationship('TeamScore', back_populates='test')

class TeamScore(Base):
    __tablename__ = 'team_scores'
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    score = Column(Integer, nullable=False)
    
    team = relationship('Team', back_populates='scores')
    test = relationship('Test', back_populates='scores')

# Deprecated
class FootballResult(Base):
    __tablename__ = 'football_results'
    id = Column(Integer, primary_key=True, index=True)
    team= Column(String, nullable=False)
    score = Column(Integer, nullable=False)
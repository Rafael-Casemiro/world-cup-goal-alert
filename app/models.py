from sqlalchemy import Column
from operator import index
from sqlalchemy import String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Team(Base):
     __tablename__ = "teams"
     id = Column(Integer, primary_key=True, index=True)
     name = Column(String, index=True)
     logo_url = Column(String, nullable=True)


class Match(Base):
     __tablename__ = "matches"
     id = Column(Integer, primary_key=True, index=True)
     home_team_id = Column()
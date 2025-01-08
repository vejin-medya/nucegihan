from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os



# Base class for our ORM models
Base = declarative_base()

# Define the News model
class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(Text, unique=True, nullable=False)
    headline = Column(Text, nullable=False)
    image_url = Column(Text)
    publish_date = Column(String)
    site_name = Column(String)



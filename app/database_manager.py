import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(Text, unique=True)
    headline = Column(Text)
    image_url = Column(Text)
    publish_date = Column(String)
    site_name = Column(Text)

    __table_args__ = (UniqueConstraint('link', name='uix_1'),)

class DatabaseManager:
    def __init__(self):
        # Get the DATABASE_URL from environment (Heroku provides this automatically)
        self.db_url = os.getenv('DATABASE_URL', 'sqlite:///news.db')  # Fallback for local testing
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)  # Create tables
        self.Session = sessionmaker(bind=self.engine)

    def save_news(self, data):
        session = self.Session()
        try:
            for news_item in data:
                news_entry = News(
                    link=news_item['link'],
                    headline=news_item['headline'],
                    image_url=news_item['image_url'],
                    publish_date=news_item['publish_date'],
                    site_name=news_item['site_name']
                )
                session.add(news_entry)
            session.commit()
        except IntegrityError:  # Handle duplicate entries
            session.rollback()
        finally:
            session.close()

    def get_news(self, site=None, since=None):
        session = self.Session()
        query = session.query(News)
        
        if site:
            query = query.filter(News.site_name == site)
        if since:
            query = query.filter(News.publish_date > since)
        
        news = query.order_by(News.publish_date.desc()).limit(200).all()
        session.close()

        return [news_item.__dict__ for news_item in news]
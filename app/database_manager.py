import os
from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert as pg_insert
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
    def __init__(self, db_url):
        # Initialize SQLAlchemy engine and session factory
        self.engine = create_engine(db_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)
    def create_tables(self,db_url):
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    def save_news(self, data):
        """Saves a list of news items to the PostgreSQL database."""
        session = self.Session()
        try:
            # Batch insert with ON CONFLICT DO NOTHING
            stmt = pg_insert(News).values(data).on_conflict_do_nothing()
            session.execute(stmt)
            session.commit()
            print("News saved successfully.")
        except IntegrityError as e:
            print(f"Integrity error while saving news: {e}")
            session.rollback()
        except Exception as e:
            print(f"Unexpected error while saving news: {e}")
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
        news = query.order_by(News.publish_date.desc()).limit(300).all()
        session.close()
        return [news_item.__dict__ for news_item in news]

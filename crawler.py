from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///web_crawler.db')

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Website(Base):
    __tablename__ = 'websites'
    website_id = Column(Integer, primary_key=True)
    location = Column(String)
    server = Column(String)


Base.metadata.create_all(engine)



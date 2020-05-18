from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import requests
from contextlib import contextmanager
from bs4 import BeautifulSoup


engine = create_engine('sqlite:///web_crawler.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Website(Base):
    __tablename__ = 'websites'
    website_id = Column(Integer, primary_key=True)
    location = Column(String)
    server = Column(String)


Base.metadata.create_all(engine)

def main():

    url = 'http://register.start.bg/'
    r = requests.get(url)
    server = r.headers["Server"]
    website = Website(location=url, server=server)

    with session_scope() as session:
        session.add(website)

    queue = [url]

    while len(queue):
        queue.remove(queue[0])

    html = r.content.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    for link in soup.find_all('a'):
        a = str(link.get('href'))
        if a.startswith('http'):
            queue.append(a)
            # print(a)


if __name__ == '__main__':
    main()

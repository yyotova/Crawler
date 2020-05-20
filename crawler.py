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

    with session_scope() as session:
        url = 'http://register.start.bg/'
        queue = [url]

        while len(queue):
            next_url = queue[0]
            queue.remove(queue[0])
            try:
                r = requests.get(next_url)
            except requests.exceptions.ConnectionError:
                continue

            server = r.headers["Server"]
            website = Website(location=next_url, server=server)
            result_in_db = session.query(Website).filter(Website.location == next_url).first()
            if result_in_db is None:
                session.add(website)
                session.commit()

            try:
                html = r.content.decode('utf-8')
            except UnicodeDecodeError:
                pass
            finally:
                soup = BeautifulSoup(html, 'html.parser')

                for link in soup.find_all('a'):
                    link = str(link.get('href'))
                    if link.startswith('http'):
                        queue.append(link)
                        print(link)
                    elif link is not None and not link.startswith('#'):
                        link = url + link
                        queue.append(link)
                        print(link)


if __name__ == '__main__':
    main()

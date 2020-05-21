from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import requests
from contextlib import contextmanager
from bs4 import BeautifulSoup
import sys
import datetime
from analitic_chart import show_chart


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
    crawled_at = Column(String)


Base.metadata.create_all(engine)


def menu():
    print(f'''
        Choose option:
        1. How many links are visited in last [time range]?
        2. How many unique domains visited in last [time range]?
        ''')


str_range = []
visited = []


def last_visited(time_range):
    global str_range
    global visited
    with session_scope() as session:
        if time_range[1] in ['hour', 'hours']:
            time = datetime.datetime.now() - datetime.timedelta(hours=int(time_range[0]))
            str_range.append(f'{str(datetime.datetime.now())[:19]} - {str(time)[:19]}')
            websites = session.query(Website).filter(Website.crawled_at > time).all()
            visited.append(len(websites))
            return len(websites)
        elif time_range[1] in ['day', 'days']:
            time = datetime.datetime.now() - datetime.timedelta(days=int(time_range[0]))
            str_range.append(f'{str(datetime.datetime.now())[:19]} - {str(time)[:19]}')
            websites = session.query(Website).filter(Website.crawled_at > time).all()
            visited.append(len(websites))
            return len(websites)
        elif time_range[1] == 'seconds':
            time = datetime.datetime.now() - datetime.timedelta(seconds=int(time_range[0]))
            str_range.append(f'{str(datetime.datetime.now())[:19]} - {str(time)[:19]}')
            websites = session.query(Website).filter(Website.crawled_at > time).all()
            visited.append(len(websites))
            return len(websites)
        elif time_range[1] in ['year', 'years']:
            time = datetime.datetime.now() - datetime.timedelta(years=int(time_range[0]))
            str_range.append(f'{str(datetime.datetime.now())[:19]} - {str(time)[:19]}')
            websites = session.query(Website).filter(Website.crawled_at > time).all()
            visited.append(len(websites))
            return len(websites)


def histogram():
    with session_scope() as session:
        servers = session.query(Website).all()
        for s in servers:
            print(s.server)


def main():
    with session_scope() as session:
        url = 'http://register.start.bg/'
        web = session.query(Website).order_by(Website.website_id.desc()).first()
        if web is None:
            queue = [url]
        else:
            queue = [web.location]

        print(queue)
        while len(queue):
            next_url = queue[0]
            queue.remove(queue[0])
            try:
                r = requests.get(next_url)
            except requests.exceptions.ConnectionError:
                continue

            server = r.headers["Server"]
            website = Website(location=next_url, server=server, crawled_at=datetime.datetime.now())
            result_in_db = session.query(Website).filter(Website.location == next_url).first()
            if result_in_db is None:
                session.add(website)
                session.commit()

            try:
                html = r.content.decode('utf-8')
            except UnicodeDecodeError:
                continue
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
    try:
        command = input('Crawler, Histogram or Analitics: ')
        if command == 'c':
            main()
        elif command == 'h':
            print('\n HISTOGRAM: \n')
            histogram()
        elif command == 'a':
            menu()
            option = input('Option: ')
            if option == '1':
                exit = False
                while not exit:
                    range_time = input('Enter time range: ')
                    time = range_time.split(' ')
                    print('Visited websites:', last_visited(time))
                    if input('One more time range? ') in ['no', 'n']:
                        exit = True
                chart = input('Do you want a chart? ')
                if chart in ['yes', 'y']:
                    show_chart(str_range, visited)
    except KeyboardInterrupt:
        sys.exit(0)

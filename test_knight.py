import pytest
import psycopg2
from contextlib import closing
from pyramid import testing
import sqlalchemy as sa
import os
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base

TEST_DSN = 'dbname=test user=edward'
AL_TEST_DSN = 'postgresql://edward:@/test'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS comment (
    id serial PRIMARY KEY,
    text TEXT NOT NULL,
    username VARCHAR (127) NOT NULL,
    reddit BOOLEAN NOT NULL,
    permalink VARCHAR (127) NOT NULL,
    approved BOOLEAN NOT NULL
)
"""

@pytest.fixture(scope='session')
def db(request):
    """set up test database"""
    settings = {'db': TEST_DSN}
    with closing(connect_db(settings)) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()

    def cleanup():
        with closing(connect_db(settings)) as db:
            db.cursor().execute("DROP TABLE comment")
            db.commit()

    request.addfinalizer(cleanup)

    return settings

# def init_db(settings):
#     import pdb; pdb.set_trace()
#     with closing(connect_db(settings)) as db:
#         db.cursor().execute(DB_SCHEMA)
#         db.commit()

# def clear_db(settings):
#     with closing(connect_db(settings)) as db:
#         db.cursor().execute("DROP TABLE entries")
#         db.commit()

def connect_db(settings):
    """Return a connection to the configured database"""
    return psycopg2.connect(settings['db'])

@pytest.fixture(scope='function')
def app(db):
    from whiteapp import main
    from webtest import TestApp
    import os
    os.environ['DATABASE_URL'] = AL_TEST_DSN
    app = main()
    return TestApp(app)

@pytest.yield_fixture(scope='function')
def req_context(db, request):
    """mock a request with a database attached"""
    settings = db
    req = testing.DummyRequest()
    with closing(connect_db(settings)) as db:
        req.db = db
        req.exception = None
        yield req

def run_query(db, query, params=(), get_results=True):
    cursor = db.cursor()
    cursor.execute(query, params)
    db.commit()
    results = None
    if get_results:
        results = cursor.fetchall()
    return results

comments ={}

def test_reddit_scraper():
    from scraper import get_comments
    comments = get_comments('whiteknighttest', 7)
    for num in comments:
        if comments[num]['text'] == 'Shit':
            assert comments[num]['text'] == 'Shit'

def test_scrape_reddit(app):
    # assert that there are no entries when we start
    rows = run_query(req_context.db, "SELECT * FROM comment")
    assert len(rows) == 0

    # add comments from whiteknighttest to database
    entry_data = {
        'subreddit': 'whiteknighttest',
        'sub_number': 7,
    }
    response = app.post('/scrape', params=entry_data, status='3*')

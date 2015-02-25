import pytest
import psycopg2
from contextlib import closing
from pyramid import testing

TEST_DSN = 'dbname=test user=edward'

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
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
    """set up and tear down a database"""
    settings = {'db': TEST_DSN}
    init_db(settings)

    def cleanup():
        clear_db(settings)

    request.addfinalizer(cleanup)

    return settings

def init_db(settings):
    with closing(connect_db(settings)) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()

def clear_db(settings):
    with closing(connect_db(settings)) as db:
        db.cursor().execute("DROP TABLE entries")
        db.commit()

def connect_db(settings):
    """Return a connection to the configured database"""
    return psycopg2.connect(settings['db'])

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

def test_scrape_reddit(req_context):
    from whiteapp import scrape_reddit
    fields = ('subreddit', 'sub_number')
    values = ('whiteknighttest', 7)
    req_context.params = dict(zip(fields, values))

    # assert that there are no entries when we start
    rows = run_query(req_context.db, "SELECT * FROM entries")
    assert len(rows) == 0

    # add comments from whiteknighttest to database
    scrape_reddit(req_context)

    rows = run_query(req_context.db, "SELECT username, text, permalink FROM entries")
    assert len(rows) == 1

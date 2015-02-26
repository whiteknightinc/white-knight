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
from cryptacular.bcrypt import BCRYPTPasswordManager
import mock
import scraper
import whiteapp
import praw


class FakeComment(object):
    class Author(object):
        def __init__(self, name):
            self.name = name

    def __init__(self, body, author, permalink):
        super(FakeComment, self).__init__()
        self.body = body
        self.author = self.Author(author)
        self.permalink = permalink

@pytest.fixture(scope='session')
def generate_fr():
    c1 = FakeComment(u'safe', u'Tom', u'www.site1.com')
    c2 = FakeComment(u'should be safe', u'Dick', u'www.site2.com')
    c3 = FakeComment(u'Fucking not safe at Fucking all, Shit Shit Shit', u'Harry', u'www.site3.com')
    return [c1, c2, c3]


def test_t_scraper(generate_fr):

    test_scraper = scraper
    test_scraper.from_reddit = mock.Mock(return_value=generate_fr)
    comments = test_scraper.get_comments('gaming', 100)
    assert len(comments) == 1
    assert comments[0]['text'] == u'Fucking not safe at Fucking all, Shit Shit Shit'
    whiteapp.get_comments = mock.Mock(side_effect=praw.errors.RedirectException)
    whiteapp.get_comments_from_reddit('theredpill', 100)


TEST_DSN = 'dbname=test_learning_journal user=roberthaskell'
AL_TEST_DSN = 'postgresql://roberthaskell:@/test_learning_journal'
# TEST_DSN = 'dbname=test_learning_journal user=roberthaskell'
# AL_TEST_DSN = 'postgresql://roberthaskell:@/test_learning_journal'

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
def authorize():
    login_data = {'username': 'admin', 'password': 'secret'}
    return app.post('/login', params=login_data, status='*')

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

@pytest.fixture(scope='function')
def auth_req(request):
    manager = BCRYPTPasswordManager()
    settings = {
        'auth.username': 'admin',
        'auth.password': manager.encode('secret'),
    }
    testing.setUp(settings=settings)
    req = testing.DummyRequest()

    def cleanup():
        testing.tearDown()

    request.addfinalizer(cleanup)

    return req

def test_do_login_success(auth_req):
    from whiteapp import do_login
    auth_req.params = {'username': 'admin', 'password': 'secret'}
    assert do_login(auth_req)

comments ={}

def test_reddit_scraper():
    from scraper import get_comments
    import praw
    comments = get_comments('whiteknighttest', 7)
    for num in comments:
        if comments[num]['text'] == 'Shit':
            assert comments[num]['text'] == 'Shit'


def test_scrape_reddit(req_context, app, auth_req):
    from whiteapp import feed
    # assert that there are no entries when we start
    rows = run_query(req_context.db, "SELECT * FROM comment")
    assert len(rows) == 0

    # add comments from whiteknighttest to database
    entry_data = {
        'subreddit': 'whiteknighttest',
        'sub_number': 7,
    }
    app.post('/scrape', params=entry_data, status='3*')
    auth_req.params = {'username': 'admin', 'password': 'secret'}
    db_comments = feed(auth_req)
    for num in comments:
        assert comments[num] in db_comments

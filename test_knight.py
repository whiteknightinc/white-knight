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
import requests
from tweepy import TweepError
from whiteapp import Comments


TEST_DSN = 'dbname=test_learning_journal user=roberthaskell'
AL_TEST_DSN = 'postgresql://roberthaskell:@/test_learning_journal'

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


def test_create(req_context, app, auth_req):
    # assert that there are no entries when we start
    run_query(req_context.db, "TRUNCATE comment", get_results=False)
    Comments.create({'text': u'test', 'user': u'testuser', 'permalink': u'testperma'}, reddit=True)
    rows = run_query(req_context.db, "SELECT * FROM comment")
    assert len(rows) == 1
    assert rows[0] == (1, 'test', 'testuser', True, 'testperma', False)


def test_reddit_connection():
    whiteapp.get_comments = mock.Mock(side_effect=requests.ConnectionError('connection error'))
    with pytest.raises(requests.ConnectionError):
        assert whiteapp.get_comments()


def test_twitter_connection():
    whiteapp.get_nasty_tweets = mock.Mock(side_effect=requests.ConnectionError('connection error'))
    with pytest.raises(requests.ConnectionError):
        assert whiteapp.get_nasty_tweets()

def test_getting_correct_comments(generate_fr):
    test_scraper = scraper
    test_scraper.from_reddit = mock.Mock(return_value=generate_fr)
    comments = test_scraper.get_comments('gaming', 100)
    assert len(comments) == 1
    assert comments[0]['text'] == u'Fucking not safe at Fucking all, Shit Shit Shit'


def test_approve_comment():
    pass


def test_remove_all():
    pass


def test_edit():
    pass


def tweet_comment():
    pass


def scrape_twitter():
    pass


def scrape_reddit():
    pass

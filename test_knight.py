import pytest
import psycopg2
from contextlib import closing

TEST_DSN = 'dbname=test user=edward'

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id serial PRIMARY KEY,
    text TEXT NOT NULL,
    username VARCHAR (127) NOT NULL,
    reddit BOOLEAN NOT NULL,
    permalink VARCHAR (127) NOT NULL
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
    with closing(psycopg2.connect(settings['db'])) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()

def clear_db(settings):
    with closing(psycopg2.connect(settings['db'])) as db:
        db.cursor().execute("DROP TABLE entries")
        db.commit()

def test_get_comments_from_reddit():
    pass

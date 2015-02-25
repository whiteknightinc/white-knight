import sqlalchemy as sa
import transaction
# import praw
import os
from scraper import get_comments
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from waitress import serve
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Comments(Base):
    __tablename__ = 'comment'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.UnicodeText, nullable=False)
    username = sa.Column(sa.Unicode(127), nullable=False)
    reddit = sa.Column(sa.Boolean, nullable=False)
    permalink = sa.Column(sa.Unicode(127), nullable=False)

    @classmethod
    def create(cls, comment, reddit):
        text = comment['text']
        username = comment['user']
        permalink = comment['permalink']
        reddit = reddit
        new_entry = cls(text=text, username=username, reddit=reddit, permalink=permalink)
        DBSession.add(new_entry)
        transaction.commit()

    @classmethod
    def all(cls):
        return DBSession.query(cls).order_by(cls.id).all()

def get_comments_from_reddit():
    comments = get_comments()
    for comment in comments:
        if not has_entry(comments[comment]['permalink']):
            Comments.create(comments[comment], reddit=True)

def has_entry(permalink):
        # dictionary of permalinks
        entries = Comments.all()
        for entry in entries:
            if entry.permalink == permalink:
                return True
        return False

def main():
    settings = {}
    settings['sqlalchemy.url'] = os.environ.get(
        ### FIX THE DB URL FORMAT, MUST BE rfc1738 URL
        'DATABASE_URL', 'postgresql:///whiteknight'
    )
    engine = sa.engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    get_comments_from_reddit()

if __name__ == '__main__':
    app = main()

# from sqlalchemy import create_engine
# engine = create_engine('postgresql://edward:@/whiteknight')
# engine = create_engine('postgresql+psycopg2://scott:tiger@localhost/mydatabase')

import sqlalchemy as sa
import praw
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
    user = sa.Column(sa.UnicodeText, nullable=False)
    reddit = sa.Column(sa.Boolean, nullable=False)
    permalink = sa.Column(sa.String, nullable=False)

    @classmethod
    def create(cls, comment, reddit):
        text = comment.body
        user = comment.author
        reddit = reddit
        permalink = comment.permalink
        new_entry = cls(text=text, user=user, reddit=reddit, permalink=permalink)
        DBSession.add(new_entry)

def get_comments_from_reddit():
    Comments.create(get_comments, reddit=True)

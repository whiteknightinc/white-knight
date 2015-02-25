import pytest
import psycopg2
from contextlib import closing
from pyramid import testing
from whiteapp import Comments

def test_add_Comments():

    new_comment = {
    'text': 'testext',
    'user': 'testusername',
    'permalink': 'www.testperma.com'
    }

    Comments.create(new_comment, False)

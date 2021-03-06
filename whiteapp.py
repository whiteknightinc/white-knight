from pyramid.session import SignedCookieSessionFactory
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from cryptacular.bcrypt import BCRYPTPasswordManager
from waitress import serve
from tweepy import TweepError
import sqlalchemy as sa
import os
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base
from scraper import get_comments
from twitter_scraper import get_nasty_tweets
from twitter_scraper import tweet_it_out
from requests import ConnectionError
import requests

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

here = os.path.dirname(os.path.abspath(__file__))

post_count = 0
source_name = ''
timeout = False

class Comments(Base):
    __tablename__ = 'comment'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.UnicodeText, nullable=False)
    username = sa.Column(sa.Unicode(127), nullable=False)
    reddit = sa.Column(sa.Boolean, nullable=False)
    permalink = sa.Column(sa.Unicode(127), nullable=False)
    approved = sa.Column(sa.Boolean, nullable=False)

    @classmethod
    def create(cls, comment, reddit):
        """Create a post with the attributes specified in scraper."""
        text = comment['text']
        username = comment['user']
        permalink = comment['permalink']
        reddit = reddit
        new_entry = cls(text=text,
                        username=username,
                        reddit=reddit,
                        permalink=permalink,
                        approved=False
                        )
        DBSession.add(new_entry)

    @classmethod
    def all(cls):
        """Return all posts in a descending order."""
        return DBSession.query(cls).order_by(cls.id.desc()).all()

    @classmethod
    def home(cls):
        """Return only approved posts in descending order limiting to 5."""
        return DBSession.query(cls).filter(cls.approved).\
            order_by(cls.id.desc()).limit(5)

    @classmethod
    def by_id(cls, id):
        """Return one post by its id."""
        return DBSession.query(cls).filter(cls.id == id).one()

    @classmethod
    def delete_by_id(cls, id):
        """Remove a post based on its id."""
        comment = DBSession.query(cls).filter(cls.id == id).one()
        DBSession.delete(comment)

    @classmethod
    def approve_comment(cls, id):
        """Change the posts value for 'Approved' to 'True'."""
        comment = DBSession.query(cls).filter(cls.id == id).one()
        comment.approved = True


def has_entry(permalink):
    """Determine if a post has a permalink or not."""
    entries = Comments.all()
    for entry in entries:
        if entry.permalink == permalink:
            return True
    return False


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    """Return the 5 most recently tweeted posts."""
    return {'comments': Comments.home()}


@view_config(route_name='feed', renderer='templates/feed.jinja2')
def feed(request):
    """Return the scraped objects from Reddit and Twitter if logged in."""
    global post_count
    global source_name
    global timeout
    if request.authenticated_userid:
        return {'comments': Comments.all(),
                'post_count': post_count,
                'source_name': source_name,
                'timeout': timeout
                }
    else:
        return HTTPForbidden()


@view_config(route_name='scrape_twitter', request_method='POST')
def scrape_twitter(request):
    """Scrape over Twitter for posts that fit the parameters establshed."""
    global timeout
    timeout = False
    handle = request.params.get('handle', None)
    if handle == "":
        handle = 'DouserBot'
    try:
        tweet_number = int(request.params.get('tweet_number', None))
    except TypeError:
        tweet_number = 100
    get_tweets(handle, tweet_number)
    return HTTPFound(request.route_url('feed'))


def get_tweets(handle, tweet_number):
    """
    Run the scraper over Twitter with a
    defined number of tweets and a
    specified account.
    """
    global source_name
    try:
        tweets = get_nasty_tweets(handle, tweet_number)
        if handle == "":
            source_name = "DouserBot's feed"
        else:
            source_name = handle
        global post_count
        post_count = len(tweets)
        for tweet in tweets:
            if not has_entry(tweets[tweet]['permalink']):
                Comments.create(tweets[tweet], reddit=False)
    except TweepError:
        source_name = handle
        return {}


@view_config(route_name='scrape', request_method='POST')
def scrape_reddit(request):
    """Scrape over Reddit for posts that fit the parameters establshed."""
    global timeout
    timeout = False
    subreddit = request.params.get('subreddit', None)
    if subreddit == "":
        subreddit = 'all'
    try:
        subnumber = int(request.params.get('sub_number', None))
    except TypeError:
        subnumber = 100
    get_comments_from_reddit(subreddit, subnumber, request)
    return HTTPFound(request.route_url('feed'))


def get_comments_from_reddit(subreddit, subnumber, request):
    """
    Run the scraper over Reddit with a
    defined number of comments and a
    specified subreddit.
    """
    try:
        comments, timeoutbool = get_comments(subreddit, subnumber)
    except ConnectionError:
        raise ConnectionError('connection error')
    counter = 0
    for comment in comments:
        if not has_entry(comments[comment]['permalink']):
            counter += 1
            Comments.create(comments[comment], reddit=True)
    if timeoutbool:
        global timeout
        timeout = True
    global source_name
    source_name = subreddit
    global post_count
    post_count = counter


@view_config(route_name="tweet")
def tweet_comment(request):
    """Tweet out a specified post."""
    try:
        tweet_it_out(request.params.get('text', "ignore this tweet"))
        Comments.approve_comment(request.matchdict.get('id', -1))
        return HTTPFound(request.route_url('feed'))
    except TweepError:
        return HTTPFound(request.route_url('edit_comment', id=request.matchdict.get('id', -1)))


@view_config(route_name='edit_comment',
             renderer='templates/editcomment.jinja2'
             )
def edit(request):
    """Allow for editing of a post before Tweeting it out."""
    entry = {'entries': [Comments.by_id(request.matchdict.get('id', -1))]}
    if request.method == 'POST':
        edit = entry['entries'][0]
        edit.title = request.params['title']
        edit.text = request.params['text']
    return entry


@view_config(route_name='remove_one')
def remove(request):
    entry = Comments.by_id(request.matchdict.get('id', -1))
    Comments.delete_by_id(entry.id)
    return HTTPFound(request.route_url('home'))


@view_config(route_name='delete_all')
def delete(request):
    """Delete all unapproved comments from the admin feed."""
    comments = Comments.all()
    for comment in comments:
        if not comment.approved:
            Comments.delete_by_id(comment.id)
    return HTTPFound(request.route_url('feed'))


@view_config(route_name='login', renderer="templates/login.jinja2")
def login(request):
    """authenticate a user by username/password"""
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = "Login Failed"
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as val_err:
            error = str(val_err)

        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'error': error, 'username': username}


def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('both username and password are required')

    settings = request.registry.settings
    manager = BCRYPTPasswordManager()
    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')
        return manager.check(hashed, password)


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


def main():
    """Create a configured wsgi app"""
    settings = {}
    settings['reload_all'] = os.environ.get('DEBUG', True)
    settings['debug_all'] = os.environ.get('DEBUG', True)
    settings['sqlalchemy.url'] = os.environ.get(
        'DATABASE_URL', 'postgresql:///whiteknight'
    )
    engine = sa.engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    manager = BCRYPTPasswordManager()
    settings['auth.password'] = os.environ.get(
        'AUTH_PASSWORD', manager.encode('secret')
    )
    secret = os.environ.get('JOURNAL_SESSION_SECRET', 'itsaseekrit')
    session_factory = SignedCookieSessionFactory(secret)
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'anotherseekrit')
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512',
            debug=True
        ),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.add_static_view('static', os.path.join(here, 'static'))
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('feed', '/feed')
    config.add_route('scrape', '/scrape')
    config.add_route('scrape_twitter', '/scrape_twitter')
    config.add_route('tweet', '/tweet/{id}')
    config.add_route('edit_comment', '/edit_comment/{id}')
    config.add_route('remove_one', '/remove_one/{id}')
    config.add_route('delete_all', '/delete_all')
    config.scan()
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    main = main()
    serve(main, host='0.0.0.0', port=8080)

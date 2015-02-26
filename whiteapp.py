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
import transaction
from sqlalchemy.ext.declarative import declarative_base
from scraper import get_comments
from twitter_scraper import get_nasty_tweets
from twitter_scraper import tweet_it_out


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

here = os.path.dirname(os.path.abspath(__file__))
post_count = 0
source_name = ''


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    return {'comments': Comments.home()}


def read_one_comment():
    return {'comments': Comments.all()}


@view_config(route_name='feed', renderer='templates/feed.jinja2')
def feed(request):
    global post_count
    global source_name
    if request.authenticated_userid:
        return {'comments': Comments.all(), 'post_count': post_count, 'source_name': source_name}
    else:
        return HTTPForbidden()


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
        transaction.commit()

    @classmethod
    def all(cls):
        return DBSession.query(cls).order_by(cls.id.desc()).all()

    @classmethod
    def home(cls):
        return DBSession.query(cls).filter(cls.approved).order_by(cls.id.desc()).limit(5)

    @classmethod
    def by_id(cls, id):
        return DBSession.query(cls).filter(cls.id == id).one()

    @classmethod
    def delete_by_id(cls, id):
        comment = DBSession.query(cls).filter(cls.id == id).one()
        DBSession.delete(comment)

    @classmethod
    def approve_comment(cls, id):
        comment = DBSession.query(cls).filter(cls.id == id).one()
        comment.approved = True
        transaction.commit()


def get_comments_from_reddit(subreddit, subnumber):
    comments = get_comments(subreddit, subnumber)
    counter = 0
    for comment in comments:
        if not has_entry(comments[comment]['permalink']):
            counter += 1
            Comments.create(comments[comment], reddit=True)
    global source_name
    source_name = subreddit
    global post_count
    post_count = counter


def get_tweets(handle, tweet_number):
    try:
        tweets = get_nasty_tweets(handle, tweet_number)
        global source_name
        source_name = handle
        global post_count
        post_count = len(tweets)
        for tweet in tweets:
            if not has_entry(tweets[tweet]['permalink']):
                Comments.create(tweets[tweet], reddit=False)
    except TweepError:
        return {}


def has_entry(permalink):
        # dictionary of permalinks
        entries = Comments.all()
        for entry in entries:
            if entry.permalink == permalink:
                return True
        return False


# def remove_entry(id):
#     id = comment.id
#     entry = Comments.query.get(id)
#     DBSession.


def get_entries():
    entries = Comments.all()
    return {'entries': entries}


@view_config(route_name='scrape_twitter', request_method='POST')
def scrape_twitter(request):
    handle = request.params.get('handle', None)
    if handle == "":
        handle = 'DouserBot'
    tweet_number = int(request.params.get('tweet_number', None))
    get_tweets(handle, tweet_number)
    return HTTPFound(request.route_url('feed'))


@view_config(route_name='scrape', request_method='POST')
def scrape_reddit(request):
    subreddit = request.params.get('subreddit', None)
    if subreddit == "":
        subreddit = 'all'
    subnumber = int(request.params.get('sub_number', None))
    get_comments_from_reddit(subreddit, subnumber)
    return HTTPFound(request.route_url('feed'))


@view_config(route_name="tweet")
def tweet_comment(request):
    tweet_it_out(request.params.get('text', "ignore this tweet"))
    Comments.approve_comment(request.matchdict.get('id', -1))
    return HTTPFound(request.route_url('feed'))


@view_config(route_name='edit_comment', renderer='templates/editcomment.jinja2')
def edit(request):
    entry = {'entries': [Comments.by_id(request.matchdict.get('id', -1))]}
    if request.method == 'POST':
        edit = entry['entries'][0]
        edit.title = request.params['title']
        edit.text = request.params['text']
        # update(request, request.matchdict.get('id', -1))
    return entry


@view_config(route_name='delete_all')
def delete(request):
    comments = Comments.all()
    for comment in comments:
        if not comment.approved:
            Comments.delete_by_id(comment.id)
    transaction.commit()
    return HTTPFound(request.route_url('feed'))


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
    # add a secret value for auth tkt signing
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'anotherseekrit')
    # configuration setup
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
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('feed', '/feed')
    config.add_route('scrape', '/scrape')
    config.add_route('scrape_twitter', '/scrape_twitter')
    config.add_route('tweet', '/tweet/{id}')
    config.add_route('edit_comment', '/edit_comment/{id}')
    config.add_route('delete_all', '/delete_all')
    config.scan()
    app = config.make_wsgi_app()
    return app


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


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)

if __name__ == '__main__':
    # config.add_view(hello_world, route_name='hello')
    main = main()
    serve(main, host='0.0.0.0', port=8080)

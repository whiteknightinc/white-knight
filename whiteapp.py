from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from waitress import serve
import os
import jinja2


here = os.path.dirname(os.path.abspath(__file__))


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    return {}


def hello_world(request):
    print('Incoming request')
    return Response('<body><h1>Hello World! What?</h1></body>')


def app():
    config = Configurator()
    config.add_static_view('static', os.path.join(here, 'static'))
    config.include('pyramid_jinja2')
    config.add_route('home', '/')
    config.scan()
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    # config.add_view(hello_world, route_name='hello')
    app = app()
    serve(app, host='0.0.0.0', port=8080)

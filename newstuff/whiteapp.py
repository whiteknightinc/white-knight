from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
import jinja2


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    return {}

def hello_world(request):
    print('Incoming request')
    return Response('<body><h1>Hello World! What?</h1></body>')


def app():
    config = Configurator()
    config.include('pyramid_jinja2')
    config.add_route('home', '/')
    config.scan()
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':

    # config.add_view(hello_world, route_name='hello')
    app = app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

import pkg_resources

from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from surebro.content import Site

import transaction


def make_app(global_config, **local_config):
    settings = global_config.copy()
    settings.update(local_config)
    config = Configurator(settings=settings, root_factory=root_factory)
    config.include('pyramid_tm')
    config.include('pyramid_zodbconn')
    config.scan('surebro')
    config.add_static_view('static', 'static')

    return config.make_wsgi_app()


def root_factory(request):
    connection = get_connection(request)
    root = connection.root()
    if not 'site' in root:
        root['site'] = site = Site(u'Sure, Bro!',
            u'Welcome to your new brochure site!\n'
            u'----------------------------------\n'
            u'\n'
            u'I hope you are enjoying the demo!')
        site.upload_image('image/gif',
            pkg_resources.resource_stream('surebro', 'static/pyramid-ufo.gif'))
        transaction.commit()

    return root['site']

import pkg_resources

from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from surebro.content import Page
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
        root['site'] = site = Site(u'Sure, Bro!', front_page)
        site.upload_image('image/gif',
            pkg_resources.resource_stream('surebro', 'static/pyramid-ufo.gif'))
        site['example_page'] = Page('Example Page', example_page)
        transaction.commit()

    return root['site']


front_page = u"""\
Welcome to your new brochure site!
----------------------------------

When editing a page, the text is in
`reStructuredText <http://docutils.sourceforge.net/rst.html>`_.  Click
'Edit this page' below to see this page's reStructuredText.

Links
-----

Document paths that are enclosed in double square brackets are expanded into
full URLs automatically:

`Here is an example <[[example_page]]>`_.

To create a new page, just create a link to a page that doesn't exists:

`This document doesn't exist yet <[[another_page]]>`_.
"""

example_page = u"""\
An Example Page
---------------

- Be good.
- Do good.
- Speak good.
"""

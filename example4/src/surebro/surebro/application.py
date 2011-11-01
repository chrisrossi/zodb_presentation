from jove.interfaces import Application

import pkg_resources

from surebro.catalog import SurebroCatalog
from surebro.content import Page
from surebro.content import Site

import transaction


class Main(Application):

    def configure(self, config):
        config.scan('surebro')
        config.add_static_view('static', 'surebro:static')

    def make_site(self, home, site):
        site = Site(u'Sure, Bro!', front_page)
        site.upload_image('image/gif',
            pkg_resources.resource_stream('surebro', 'static/pyramid-ufo.gif'))
        site['example_page'] = Page('Example Page', example_page)
        catalog = home['jove_catalog'][None]
        catalog.index_doc(site)
        catalog.index_doc(site['example_page'])
        return site

    def services(self):
        return [
            ('jove_catalog#catalog', SurebroCatalog()),
        ]


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

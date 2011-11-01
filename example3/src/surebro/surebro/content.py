from docutils.core import publish_parts
from docutils.examples import html_parts

import re

from persistent import Persistent
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from repoze.folder import Folder
from shutil import copyfileobj
from ZODB.blob import Blob


page_links = re.compile('\[\[([^\]]+)\]\]')


class Page(Folder):

    def __init__(self, title, body):
        super(Page, self).__init__()
        self.title = title
        self.body = body
        self.image = None

    def upload_image(self, mimetype, fd):
        self.image = Image(mimetype, fd)

    def html(self, resource_url):

        def cook_link(match):
            path = match.groups()[0]
            try:
                if not path.startswith('/'):
                    path = '/' + path
                page = find_resource(self, path)
                if isinstance(page, Page):
                    return resource_url(page)
            except KeyError:
                pass

            return resource_url(
                find_root(self), 'add_page', query={'path': path})

        body = page_links.sub(cook_link, self.body)
        return html_parts(body, doctitle=False,
                          initial_header_level=2)['html_body']


class Image(object):

    def __init__(self, mimetype, fd):
        self.mimetype = mimetype

        blob = Blob()
        blobfd = blob.open('w')
        copyfileobj(fd, blobfd)
        blobfd.close()

        self.data = blob


class Site(Page):
    pass

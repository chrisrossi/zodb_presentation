import re

from persistent import Persistent
from repoze.folder import Folder
from shutil import copyfileobj
from ZODB.blob import Blob


class Page(Folder):

    def __init__(self, title, body):
        super(Page, self).__init__()
        self.title = title
        self.body = body
        self.image = None

    def upload_image(self, mimetype, fd):
        self.image = Image(mimetype, fd)


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

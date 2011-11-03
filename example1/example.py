import code
import sys
import transaction

from surebro.content import Page
from surebro.content import Site

from ZODB.DB import DB
from ZODB.FileStorage import FileStorage


__doc__ = """
Interactively play with an open ZODB session.  'site' is the root site object.
There are also some functions set up for you:

- add_page(name, title, body) -- Add a page to the site
- list_pages()                -- List pages in the site
- commit()                    -- Save your work
"""


storage = FileStorage('var/surebro.db', blob_dir='var/blobs')
db = DB(storage)
connection = db.open()
root = connection.root()
if not 'site' in root:
    root['site'] = Site('Sure, Bro!')
site = root['site']


def add_page(name, title, body):
    site[name] = Page(title, body)


def list_pages():
    for name, page in site.items():
        print '%s\t%s' % (name, page.title)


banner = "Python %s on %s\n%s" % (sys.version, sys.platform, __doc__)
code.interact(banner, local={
    'site': site,
    'add_page': add_page,
    'list_pages': list_pages,
    'commit': transaction.commit
})

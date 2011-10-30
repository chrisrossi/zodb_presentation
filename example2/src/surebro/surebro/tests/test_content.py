from pyramid import testing

import unittest


class TestSite(unittest.TestCase):

    def make_one(self, title):
        from surebro.content import Site as test_class
        return test_class(title)

    def test_construction(self):
        from repoze.folder import Folder
        site = self.make_one('The Title')
        self.assertEqual(site.title, 'The Title')
        self.failUnless(isinstance(site, Folder))

    def test_folderish(self):
        class Dummy(object):
            def __init__(self, value):
                self.value = value

        site = self.make_one('The Title')
        site['foo'] = Dummy('bar')
        self.assertEqual(site['foo'].value, 'bar')


class TestPage(unittest.TestCase):

    def make_one(self, title, body):
        from surebro.content import Page as test_class
        return test_class(title, body)

    def test_construction(self):
        from persistent import Persistent
        page = self.make_one('The Title', 'The Body')
        self.assertEqual(page.title, 'The Title')
        self.assertEqual(page.body, 'The Body')

    def test_upload_image(self):
        from StringIO import StringIO
        page = self.make_one(None, None)
        data = StringIO('TESTDATA')
        page.upload_image('image/test', data)
        self.assertEqual(page.image.mimetype, 'image/test')
        self.assertEqual(page.image.data.open().read(), 'TESTDATA')

    def test_html(self):
        site = testing.DummyResource()
        site['page1'] = page = self.make_one("Page One",
            "Nice page\n"
            "---------\n"
            "\n"
            "It links to `another page <[[page2]]>`_.\n"
            "It also links to a `page that doesn't exist <[[page3]]>`_\n")
        site['page2'] = testing.DummyResource()

        from pyramid.url import resource_url
        request = testing.DummyRequest()
        def url(resource, *path, **kw):
            return resource_url(resource, request, *path, **kw)

        self.assertEqual(page.html(url),
            u'<div class="document" id="nice-page">\n'
            u'<h1 class="title">Nice page</h1>\n'
            u'<p>It links to <a class="reference external" '
            u'href="http://example.com/page2/">another page</a>.\n'
            u'It also links to a <a class="reference external" '
            u'href="http://example.com/add_page?path=%2Fpage3">'
            u'page that doesn\'t exist</a></p>\n</div>\n')

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



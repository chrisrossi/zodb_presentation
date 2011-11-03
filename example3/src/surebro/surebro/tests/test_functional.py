import mock
import unittest


class FunctionalTests(unittest.TestCase):
    start_url = '/'

    def setUp(self):
        import os
        import tempfile
        self.tmp = tmp = tempfile.mkdtemp('.surebro-tests')
        data_fs = os.path.join(tmp, 'Data.fs')
        blobs = os.path.join(tmp, 'blobs')
        self.zodb_uri = 'file://%s?blobstorage_dir=%s' % (data_fs, blobs)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def make_application(self):
        import webtest
        from surebro.application import make_app
        settings = {'zodbconn.uri': self.zodb_uri}
        return webtest.TestApp(make_app(settings))

    def test_homepage_and_example_page(self):
        app = self.make_application()
        response = app.get(self.start_url)
        self.assertEqual(response.status, '200 OK')
        response = response.click('Here is an example')
        self.assertEqual(response.status, '200 OK')
        self.failUnless('Be good' in response.body)

    def test_edit_page(self):
        app = self.make_application()
        response = app.get(self.start_url)

        # Test Cancel
        response = response.click("Edit")
        self.assertEqual(response.status, '200 OK')
        form = response.forms[1]
        response = form.submit('cancel')
        self.assertEqual(response.status, '302 Found')
        response = app.get(response.location)
        self.failUnless('Welcome' in response.body)

        # Test Save
        from StringIO import StringIO
        response = response.click("Edit")
        self.assertEqual(response.status, '200 OK')
        form = response.forms[1]
        form['title'] = 'WebTest Title'
        form['body'] = 'WebTest Body'
        form['image'] = 'test.jpg', 'TEST'
        response = form.submit('save')
        self.assertEqual(response.status, '302 Found')
        response = app.get(response.location)
        self.failUnless('WebTest Title' in response.body)
        self.failUnless('WebTest Body' in response.body)

        response = app.get(response.request.url + 'image')
        self.assertEqual(response.content_type, 'image/jpeg')
        self.assertEqual(response.body, 'TEST')

        # Test Search
        response = app.get(self.start_url)
        form = response.forms[0]
        form['term'] = 'Body'
        response = form.submit()
        response = response.click('WebTest Title')
        self.failUnless('WebTest Body' in response.body)

        form = response.forms[0]
        form['term'] = 'Jabberwocky'
        response = form.submit()
        self.failUnless('No items' in response.body)

        form = response.forms[0]
        form['term'] = ''
        response = form.submit()
        self.failUnless('No items' in response.body)

    def test_add_page(self):
        app = self.make_application()
        response = app.get(self.start_url)

        # Test Cancel
        response = response.click("doesn't")
        self.assertEqual(response.status, '200 OK')
        form = response.forms[1]
        response = form.submit('cancel')
        self.assertEqual(response.status, '302 Found')
        response = app.get(response.location)
        self.failUnless('Welcome' in response.body)

        # Test Save
        response = response.click("doesn't")
        self.assertEqual(response.status, '200 OK')
        form = response.forms[1]
        form['title'] = 'WebTest Title'
        form['body'] = 'WebTest Body'
        form['image'] = 'test.jpg', 'TEST'
        response = form.submit('save')
        self.assertEqual(response.status, '302 Found')
        response = app.get(response.location)
        self.failUnless('WebTest Title' in response.body)
        self.failUnless('WebTest Body' in response.body)

        response = app.get(response.request.url + 'image')
        self.assertEqual(response.content_type, 'image/jpeg')
        self.assertEqual(response.body, 'TEST')

        # Test create page with depth
        response = app.get(self.start_url)
        response = response.click("doesn't")
        response = response.click("Edit")
        form = response.forms[1]
        form['body'] = '`One more time <[[with/feeling]]>`_'
        response = form.submit('save')
        response = app.get(response.location)
        response = response.click('One more time')
        form = response.forms[1]
        form['title'] = 'Doctor'
        form['body'] = '`Shallower <[[with]]>`_'
        response = form.submit('save')
        response = app.get(response.location)
        response = response.click('Shallower')
        form = response.forms[1]
        form['body'] = 'Italians do it better.'
        response = form.submit('save')
        response = app.get(response.location)
        self.failUnless('Italians do it better.' in response.body)
        response = response.click('Edit')
        form = response.forms[1]
        response = form.submit('cancel')
        response = app.get(response.location)
        url = response.request.url

        # Test Search
        response = app.get(self.start_url)
        form = response.forms[0]
        form['term'] = 'shallower'
        response = form.submit()
        response = response.click('Doctor')
        self.failUnless('Shallower' in response.body, response.body)

        # Delete page
        from webtest.app import AppError
        response = app.get(url)
        response = response.click('Delete')
        self.assertEqual(response.status, '302 Found')
        self.assertRaises(AppError, app.get, url)
        response = app.get(response.location)
        response = response.click("doesn't")
        response = response.click('One more time')
        response = response.click('Delete')
        response = app.get(response.location)
        self.failUnless('Here is an example' in response.body, response.body)
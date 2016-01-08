from __future__ import print_function, unicode_literals
import orloui
from orloclient.mock_orlo import MockOrlo
from orloui.config import config
from flask.ext.testing import TestCase

__author__ = 'alforbes'

orloui.orlo = MockOrlo(uri='http://localhost/dummy')
orloui.views.orlo = MockOrlo(uri='http://localhost/dummy')


class ViewTest(TestCase):
    """
    Testing the views
    """

    def create_app(self):
        app = orloui.app
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['TRAP_HTTP_EXCEPTIONS'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        return orloui.app

    def test_ping(self):
        """
        Test the /ping url
        """
        response = self.client.get('/ping')
        self.assert200(response)

    def test_home(self):
        """
        Test the home page loads
        """
        response = self.client.get('/')
        self.assert200(response)

    def test_status(self):
        """
        Test status page loads
        """
        response = self.client.get('/status')
        self.assert200(response)

    def test_releases(self):
        """
        Test /releases
        """
        response = self.client.get('/releases')
        self.assert200(response)

    def test_releases_with_id(self):
        """
        Test /releases/<id>
        """
        # Need an ID to test!
        response = self.client.get('/releases/')
        self.assert200(response)

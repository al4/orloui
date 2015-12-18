from __future__ import print_function, unicode_literals
import orloWeb
from orloclient.mock_orlo import MockOrlo
from orloWeb.config import config
from flask.ext.testing import TestCase

__author__ = 'alforbes'

orloWeb.orlo = MockOrlo(uri='http://localhost/dummy')
orloWeb.views.orlo = MockOrlo(uri='http://localhost/dummy')


class ViewTest(TestCase):
    """
    Testing the views
    """

    def create_app(self):
        app = orloWeb.app
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['TRAP_HTTP_EXCEPTIONS'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        return orloWeb.app

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


# -*- coding: utf-8; -*-

import os
from unittest import TestCase

from asgiref.wsgi import WsgiToAsgi
from pyramid.router import Router

from sideshow.web import app as mod


here = os.path.dirname(__file__)
example_conf = os.path.join(here, 'example.conf')


class TestMain(TestCase):

    def test_coverage(self):
        app = mod.main({}, **{'wutta.config': example_conf})
        self.assertIsInstance(app, Router)


class TestMakeWsgiApp(TestCase):

    def test_coverage(self):
        app = mod.make_wsgi_app()
        self.assertIsInstance(app, Router)


class TestMakeAsgiApp(TestCase):

    def test_coverage(self):
        app = mod.make_asgi_app()
        self.assertIsInstance(app, WsgiToAsgi)

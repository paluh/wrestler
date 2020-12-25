from __future__ import absolute_import
import time
import itsdangerous
import unittest
import werkzeug

from wrestler.ephemeral_routing import Map


class MapTestCase(unittest.TestCase):

    SECRET = 's3cr3t'

    def setUp(self):
        self.RULES = [werkzeug.routing.Rule('/path', endpoint='test')]

    def test_dispatcher_builds_correctly_signed_path(self):
        urls = Map(self.SECRET, 60, self.RULES)
        dispatcher = urls.bind('example.com')
        path = dispatcher.build('test')
        signer = itsdangerous.TimestampSigner(self.SECRET)
        self.assertEqual('path', signer.unsign(path.lstrip('/')))

    def test_dispatcher_builds_correctly_signed_path_for_empty_path(self):
        RULES = [werkzeug.routing.Rule('/', endpoint='test')]
        urls = Map(self.SECRET, 60, RULES)
        dispatcher = urls.bind('example.com')
        path = dispatcher.build('test')
        signer = itsdangerous.TimestampSigner(self.SECRET)
        self.assertEqual('', signer.unsign(path.lstrip('/')))

    def test_dispatcher_matches_signed_path(self):
        urls = Map(self.SECRET, 60, self.RULES)
        dispatcher = urls.bind('example.com')
        path = dispatcher.build('test')
        self.assertEqual(dispatcher.match(path), ('test', {}))

    def test_dispatcher_match_failes_when_timeout_is_exceeded(self):
        urls = Map(self.SECRET, 1, self.RULES)
        dispatcher = urls.bind('example.com')
        path = dispatcher.build('test')
        time.sleep(2)
        with self.assertRaises(itsdangerous.SignatureExpired):
            dispatcher.match(path)

    def test_demo_path_refresh_view(self):
        urls = Map(self.SECRET, 1, self.RULES)
        dispatcher = urls.bind('example.com')
        path = dispatcher.build('test')
        time.sleep(2)
        path = dispatcher.refresh(path)
        self.assertEqual(dispatcher.match(path), ('test', {}))

# test suite used in setup.py
_test_loader = unittest.TestLoader()
test_suite = _test_loader.loadTestsFromTestCase(MapTestCase)

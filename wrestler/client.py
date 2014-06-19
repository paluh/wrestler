import requests
import simplejson
import urllib
import urlparse


class ApiException(Exception):

    pass


class Client(object):

    def __init__(self, url_map, hostname, port, schema):
        self.url_map = url_map
        self.hostname = hostname
        self.port = port
        self.host = '%s:%s' % (self.hostname, self.port)
        self.schema = schema

    def _get(self, url, json=True):
        response = requests.get(url)
        if response.status_code != 200:
            raise ApiException(response=response)
        return response.content

    def _reverse(self, rule_endpoint, rule_args=None, payload=None):
        adapter = self.url_map.bind(self.host, script_name='')
        path = adapter.build(rule_endpoint, rule_args)
        if payload:
            query = urllib.urlencode(payload, doseq=True)
        else:
            query = {}
        return urlparse.urlunparse((self.schema, self.host, path, None, query, None))

    def _request(self, rule_endpoint, rule_args=None, payload=None, json=True):
        url = self._reverse(rule_endpoint, rule_args, payload)
        return self._get(url)


class JsonClient(Client):

    def _get(self, *args, **kwargs):
        response = super(JsonClient, self)._get(*args, **kwargs)
        return simplejson.loads(response)

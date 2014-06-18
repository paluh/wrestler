import itsdangerous
from urllib import unquote
from urlparse import urljoin
from werkzeug.datastructures import MultiDict
import werkzeug.routing
from werkzeug.urls import url_quote

from .application import Application

_missing = object()


class MapAdapter(werkzeug.routing.MapAdapter):

    # Unfortunately I have to copy whole method here to override it
    def build(self, endpoint, values=None, method=None, force_external=False,
              append_unknown=True):
        self.map.update()
        if values:
            if isinstance(values, MultiDict):
                valueiter = values.iteritems(multi=True)
            else:
                valueiter = values.iteritems()
            values = dict((k, v) for k, v in valueiter if v is not None)
        else:
            values = {}

        rv = self._partial_build(endpoint, values, method, append_unknown)
        if rv is None:
            raise werkzeug.routing.BuildError(endpoint, values, method)
        domain_part, path = rv

        host = self.get_host(domain_part)

        # shortcut this.
        path = self.map._sign(path.lstrip('/'))
        if not force_external and (
            (self.map.host_matching and host == self.server_name) or
            (not self.map.host_matching and domain_part == self.subdomain)):
            return str(urljoin(self.script_name, './' + path))
        return str('%s://%s%s/%s' % (
            self.url_scheme,
            host,
            self.script_name[:-1],
            path
        ))

    def match(self, path_info=None, method=None, return_rule=False,
              query_args=None):
        path_info = self.map._unsign(path_info)
        return super(MapAdapter, self).match(path_info, method, return_rule, query_args)

    def refresh(self, path_info, method=None, return_rule=False, query_args=None):
        path_info = self.map._unsign(path_info, max_age=None)
        build_params = super(MapAdapter, self).match(path_info, method, return_rule, query_args)
        return self.build(*build_params)


class Map(werkzeug.routing.Map):

    def __init__(self, secret, signature_max_age, *args, **kwargs):
        self.signer = itsdangerous.TimestampSigner(secret)
        self.signature_max_age = signature_max_age
        super(Map, self).__init__(*args, **kwargs)

    def _unsign(self, path_info=None, max_age=_missing):
        if path_info:
            path_info = path_info.lstrip('/')
            max_age=self.signature_max_age if max_age is _missing else max_age
            try:
                path_info = self.signer.unsign(path_info, max_age=max_age)
            except itsdangerous.BadSignature:
                if self.signer.sep in path_info:
                    path_info, sig = path_info.rsplit(self.signer.sep, 1)
                    path_info = self.signer.sep.join([url_quote(path_info), sig])
                    path_info = self.signer.unsign(path_info, max_age=max_age)
                else:
                    raise
            return unquote(path_info)

    def _sign(self, path_info=None):
        if path_info is not None:
            return self.signer.sign(path_info.lstrip('/'))

    def bind(self, server_name, script_name=None, subdomain=None,
             url_scheme='http', default_method='GET', path_info=None,
             query_args=None):
        path_info = self._unsign(path_info)
        server_name = server_name.lower()
        if self.host_matching:
            if subdomain is not None:
                raise RuntimeError('host matching enabled and a '
                                   'subdomain was provided')
        elif subdomain is None:
            subdomain = self.default_subdomain
        if script_name is None:
            script_name = '/'
        if isinstance(server_name, unicode):
            server_name = server_name.encode('idna')
        return MapAdapter(self, server_name, script_name, subdomain,
                          url_scheme, path_info, default_method, query_args)

    def bind_to_environ(self, environ, server_name=None, subdomain=None):
        dispatcher = super(Map, self).bind_to_environ(environ, server_name, subdomain)
        return self.bind(dispatcher.server_name, dispatcher.script_name,
                         dispatcher.subdomain, dispatcher.url_scheme,
                         dispatcher.default_method, dispatcher.path_info,
                         dispatcher.query_args)


class Application(Application):

    extra_headers = [('Cache-Control', 'no-cache, no-store, must-revalidate'),
                     ('Access-Control-Allow-Origin', '*'),
                     ('Pragma', 'no-cache'), ('Expires', '0')]

    urls = None

    def __init__(self, secret, signature_max_age, extra_headers=None):
        assert self.urls is not None, ('You have to define urls list on class '
                                       'level')
        url_map = Map(secret, signature_max_age, self.urls)
        super(Application, self).__init__(url_map, extra_headers)

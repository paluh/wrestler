import simplejson
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response


class Application(object):
    """Simple app class with basic dispatch convention - endpoint
    should corespond to method name with `serve_` prefix:

        werkzeug.routing.Rule('/profile/<int:id>',
                              endpoint='user-profile')

    above rule will be dispatched to this call (where `self`
    is Application instance):

        self.serve_user_profile(request, *args)

    P.S. you should not store any state on app instance as this is
    not thread safe.
    """

    Request = Request
    Response = Response
    # list of tuples [(header, value), ...]
    extra_headers = []
    url_map = None

    def __init__(self, url_map=None, extra_headers=None):
        self.url_map = url_map or self.url_map
        if not self.url_map:
            raise ValueError('You have to pass or define url_map value')
        self.extra_headers = extra_headers or self.extra_headers

    def __call__(self, environ, start_response):
        def _start_response(c, headers):
            response_headers = {h for h,v in headers}
            for k, v in self.extra_headers:
                if k not in response_headers:
                    headers.append((k, v))
            return start_response(c, headers)
        url_dispatcher = self.url_map.bind_to_environ(environ)
        request = self.Request(environ)
        try:
            view, args = url_dispatcher.match(request.path)
            response = self._serve(view, request, args)
        except HTTPException, e:
            response = e
        return response(environ, _start_response)

    def _serve(self, view, request, args):
        if isinstance(view, basestring):
            view_name = 'serve_%s' % view.replace('-', '_')
            if hasattr(self, view_name):
                view_method = getattr(self, view_name)
                return view_method(request, **args)
            else:
                raise ValueError('View method missing: %s' % view_name)
        raise ValueError('Base _serve implementation expects view '
                         'name as first parameter')


    def obj_to_json_response(self, obj):
        return self.Response(simplejson.dumps(obj, indent='  '),
                             mimetype='application/json')

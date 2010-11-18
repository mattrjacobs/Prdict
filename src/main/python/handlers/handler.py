"""Base functionlity for handling an HTTP request"""
import cgi
import dateutil
import httplib
import os
import urlparse

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import build
import release_number
from utils.constants import Constants

class AbstractHandler(webapp.RequestHandler):
    """Handles an HTTP request"""
    def baseurl(self):
        """Return the base URL of webapp: URI scheme + hostname"""
        parts = urlparse.urlparse(self.request.url)
        return "%s://%s" % (parts.scheme, parts.netloc)

    def render_html(self, entry, msg=None):
        """Given a single entry, render an HTML view. Optionally also add
        the given message into the view if specified."""
        raise Exception("Must be overridden by subclasses")
    
    def render_template(self, tmplt, args=None):
        """Render a template to UI, and optionally pass it arguments"""
        if not args:
            args = {}
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'templates', tmplt)
        args['build'] = "%s" % self.get_build_number()
        user = users.get_current_user()
        if not user:
            args['login_link'] = users.create_login_url("/login-receiver")
        else:
            args['logout_link'] = users.create_logout_url(self.request.uri)
        self.response.out.write(template.render(path, args))

    @staticmethod
    def get_build_number():
        return build.build_number

    @staticmethod
    def get_release_number():
        return release_number.release_number

    def set_403(self):
        """Handle a HTTP 403 - Forbidden"""
        self.response.set_status(httplib.FORBIDDEN)
        self.render_template('403.html')

    def set_404(self):
        """Handle a HTTP 404 - Not Found"""
        self.response.set_status(httplib.NOT_FOUND)
        self.render_template('404.html')

    def handle_transient_error(self):
        """Handle a HTTP 503 - Service Unavailable"""
        self.response.set_status(httplib.SERVICE_UNAVAILABLE)
        self.render_template('503.html')

    def set_header(self, header_key, header_value):
        """helper method to set an HTTP header"""
        self.response.headers[header_key] = header_value

    def get_header(self, header_key):
        """helper method to get an HTTP header"""
        if header_key in self.request.headers:
            return self.request.headers[header_key]
        return None

    @staticmethod
    def _prefers_atom_by_accept_header(acc):
        """Helper method to determine if request prefers ATOM or HTML"""
        accepts = map(lambda s: s.strip(), acc.split(','))
        prefs = {}
        for accept in accepts:
            clauses = map(lambda s: s.strip(), accept.split(';'))
            q = 1.0
            for param in clauses[1:]:
                keyval = param.split('=')
                if len(keyval) == 2 and keyval[0] == 'q':
                    try:
                        q = float(keyval[1])
                    except ValueError:
                        pass
            prefs[clauses[0]] = q
        html_pref = atom_pref = 0.0
        if '*/*' in prefs:
            html_pref = atom_pref = prefs['*/*']
            #xhtml_pref = html_pref = atom_pref = prefs['*/*']
        if 'text/*' in prefs:
            html_pref = prefs['text/*']
        if 'text/html' in prefs and 'text/xhtml' in prefs:
            html_pref = max(prefs['text/html'], prefs['text/xhtml'])
        elif 'text/html' in prefs:
            html_pref = prefs['text/html']
        elif 'text/xhtml' in prefs:
            html_pref = prefs['text/xhtml']
        if 'application/*' in prefs:
            atom_pref = prefs['application/*']
        if 'application/xml' in prefs:
            atom_pref = prefs['application/xml']
        if 'application/xhtml+xml' in prefs:
            html_pref = max(html_pref, prefs['application/xhtml+xml'])
        if 'application/atom+xml' in prefs:
            atom_pref = prefs['application/atom+xml']
        return (atom_pref > html_pref)

    def is_atom_request(self):
        """Return a pair (is_atom, vary_accept) where is_atom is true if
        the request has selected an Atom representation, and vary_accept is
        true if this was selected via the 'Accept' header (in which case
        we need to add 'Vary: Accept' to the response)."""
        query_params = cgi.parse_qs(self.request.query_string)
        if 'alt' in query_params:
            return (query_params["alt"][0] in ["xml","atom"], False)
        if 'Accept' not in self.request.headers:
            return (False, False)
        hdr = self.request.headers['Accept']
        return (self._prefers_atom_by_accept_header(hdr), True)

    def _etag_matches(self, etag):
        """Determines if given etag matches HTTP Request etag"""
        req_etags = map(lambda s: s.strip(),
                        self.request.headers['If-None-Match'].split(','))
        return (etag in req_etags)

    def _last_modified_matches(self, lm_date):
        """Determines if given last modified date is before HTTP request
        last modified date"""
        if not lm_date:
            return False
        req_lm = dateutil.parse_http_date(self.request.headers['If-Modified-Since'])
        return (req_lm >= dateutil.normalize(lm_date))

    def has_valid_data_media_type(self):
        """Determines if HTTP request has a content type that is
        form encoded."""
        content_type = self.get_header('Content-Type')
        content_types = map(lambda x: x.strip(), content_type.split(";"))
        return Constants.FORM_ENCODING in content_types

    def modified(self, etag, lm_date):
        """Return true if the data has been modified (based upon the etag
        and last modified date), or if this is an unconditional GET."""

        if ('If-None-Match' in self.request.headers
            and 'If-Modified-Since' in self.request.headers):
            return (not self._etag_matches(etag)
                    or not self._last_modified_matches(lm_date))
        elif 'If-None-Match' in self.request.headers:
            return (not self._etag_matches(etag))
        elif 'If-Modified-Since' in self.request.headers:
            return (not self._last_modified_matches(lm_date))
        return True

    #@staticmethod
    #def get_prdict_user():
    #    """Examine the current user (based upon cookie), and return it,
    #    if found.  Otherwise, return None."""
    #    cookie_user = users.get_current_user()
    #    if not cookie_user:
    #        return None
    #    else:
    #        return prdictuser.lookup_user(cookie_user)

    #def get_authorized_entry(self, key):
    #    """Retrieve the entry in question from the datastore, and check
    #    permissions. If not found, render a 404 error view.
    #    If not permitted, render a 403 view.
    #    Otherwise, return the entry in question."""
    #    user = self.get_prdict_user()
    #    if not user:
    #        self.set_403()
    #        return None
    #    try:
    #        entry = db.get(db.Key(encoded=key))
    #    except db.BadKeyError:
    #        entry = None
    #    if not entry:
    #        self.set_404()
    #        return None
    #    if not self.is_user_authorized_for_entry(user, entry):
    #        self.set_403()
    #        return None
    #    return entry

    def allow_overloaded_post_of_put_or_delete(self, key):
        """Lets a subclass handle overloaded POST of PUT or DELETE"""
        if self.request.get('_method') == 'DELETE':
            return self.delete(key)
        elif self.request.get('_method') == 'PUT':
            return self.put(key)
        self.response.set_status(httplib.BAD_REQUEST)
        msg = "POST requires either '_method=DELETE' or '_method=PUT'"
        try:
            entry = db.get(db.Key(encoded=key))
        except db.BadKeyError:
            entry = None
        self.render_html(entry, msg)

    def allow_overloaded_post_of_delete(self, key):
        """Lets a subclass handle overloaded POST of DELETE"""
        if self.request.get('_method') == 'DELETE':
            return self.delete(key)
        self.response.set_status(httplib.BAD_REQUEST)
        msg = "POST requires '_method=DELETE'"
        try:
            entry = db.get(db.Key(encoded=key))
        except db.BadKeyError:
            entry = None
        self.render_html(entry, msg)

    def in_dev_mode(self):
        """Return true iff the webapp user has a cookie set that enables
        dev-mode.  This cookie is named 'env', and the dev-mode value is
        'dev'."""

        if "env" in self.request.cookies:
            return self.request.cookies['env'] == "dev"
        return False



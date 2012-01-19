"""Base functionlity for handling an HTTP request"""
import cgi
import dateutil
import httplib
import logging
import os
import simplejson as json
import urlparse
from xml.sax.saxutils import escape

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import build
import release_number
from models import prdict_user
from utils.constants import Constants

class AbstractHandler(webapp.RequestHandler):
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    """Handles an HTTP request"""
    def baseurl(self):
        """Return the base URL of webapp: URI scheme + hostname"""
        parts = urlparse.urlparse(self.request.url)
        return self.xml_escape("%s://%s" % (parts.scheme, parts.netloc))

    def render_html(self, entry, msg=None):
        """Given a single entry, render an HTML view. Optionally also add
        the given message into the view if specified."""
        raise Exception("Must be overridden by subclasses")

    def render_string(self, s):
        self.response.out.write(s)
    
    def render_template(self, tmplt, args=None):
        """Render a template to UI, and optionally pass it arguments"""
        if not args:
            args = {}
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'templates', tmplt)
        args['build'] = "%s" % self.get_build_number()
        user = users.get_current_user()
        if not user:
            args['login_link'] = users.create_login_url("/")
        else:
            args['logout_link'] = users.create_logout_url(self.request.uri)
        self.response.out.write(template.render(path, args))

    @staticmethod
    def get_build_number():
        return build.build_number

    @staticmethod
    def get_release_number():
        return release_number.release_number

    def set_400(self, template, content_type, user, message, params = {}):
        """Returns a message explaining why entry add failed"""
        self.response.set_status(httplib.BAD_REQUEST)
        if content_type == "json":
            return self.render_string(json.dumps(
                {'status' : 'error',
                 'message' : message }))
        else:
            params.update( { 'msg' : message,
                             'current_user' : user })
            return self.render_template(template, params)

    def set_403(self, content_type, user):
        """Handle a HTTP 403 - Forbidden"""
        self.response.set_status(httplib.FORBIDDEN)
        if content_type == "atom":
            self.render_template('403.xml')
        elif content_type == "json":
            self.render_string(json.dumps({ "status" : "error",
                                            "message" : "Forbidden" }))
        else:
            self.render_template("403.html", { 'current_user' : user })

    def set_404(self, content_type, user):
        """Handle a HTTP 404 - Not Found"""
        self.response.set_status(httplib.NOT_FOUND)
        if content_type == "atom":
            self.render_template("404.xml")
        elif content_type == "json":
            self.render_string(json.dumps({ "status" : "error",
                                            "message" : "Not Found" }))
        else:
            self.render_template('404.html', { 'current_user' : user })

    def handle_transient_error(self, content_type, user):
        """Handle a HTTP 503 - Service Unavailable"""
        self.response.set_status(httplib.SERVICE_UNAVAILABLE)
        if content_type == "atom":
            self.render_template("503.xml")
        elif content_type == "json":
            self.render_string(
                json.dumps({ 'status' : 'error',
                             'message' : 'Service Unavailable' }))
        else:
            self.render_template('503.html', { 'current_user' : user })

    def set_header(self, header_key, header_value):
        """helper method to set an HTTP header"""
        self.response.headers[header_key] = header_value

    def get_header(self, header_key):
        """helper method to get an HTTP header"""
        if header_key in self.request.headers:
            return self.request.headers[header_key]
        return None

    def is_dev_host(self):
        if "SERVER_NAME" in os.environ.keys():
            server_name = os.environ["SERVER_NAME"]
            return server_name == "localhost"
        return False

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

    def is_json_request(self):
        """Return a pair (is_json, vary_accept) where is_json is true if
        the request has selected a JSON representation, and vary_accept is
        true if this was selected via the 'Accept' header (in which case
        we need to add 'Vary: Accept' to the response)."""
        query_params = cgi.parse_qs(self.request.query_string)
        if 'alt' in query_params:
            return (query_params["alt"][0] == "json", False)
        if 'Accept' not in self.request.headers:
            return (False, False)
        accept_hdr = self.request.headers['Accept']
        accept_hdrs = [s.strip() for s in accept_hdr.split(",")]
        if "application/json" in accept_hdrs:
            return (True, False)
        #Implement this later - Accept:Vary header for JSON response
        #hdr = self.request.headers['Accept']
        #return (self._prefers_json_by_accept_header(hdr), True)
        return (False, False)

    def is_form_request(self):
        content_type = self.get_header('Content-Type')
        if content_type:
            content_types = map(lambda x: x.strip(), content_type.split(";"))
            return Constants.FORM_ENCODING in content_types
        else:
            return False

    def get_read_content_type(self):
        """Returns 'atom/json/html', depending on request made"""
        (is_atom, atom_vary) = self.is_atom_request()
        if is_atom:
            return ("atom", atom_vary)
        (is_json, json_vary) = self.is_json_request()
        if is_json:
            return ("json", json_vary)
        else:
            return ("html", False)

    def get_write_content_type(self):
        """Returns 'atom/json/form', depending on request made"""
        content_type_from_req = self.get_header("Content-Type")
        if content_type_from_req:
            content_type_pieces = content_type_from_req.split(";")
            #if is_atom:
            #    return ("atom", atom_vary)
            for content_type in content_type_pieces:
                if content_type == Constants.JSON_ENCODING: 
                    return "json"
                elif content_type == Constants.FORM_ENCODING:
                    return "form"
        return "unknown"

    def get_query(self):
        query_param = self.request.get("q")
        if query_param:
            if ":" in query_param:
                return query_param.split(":", 2)
        return None

    def get_pagination_params(self):
        start_index_param = self.request.get("start-index")
        max_results_param = self.request.get("max-results")

        if start_index_param:
            try:
                start_index = int(start_index_param)
            except ValueError:
                start_index = 0
        else:
            start_index = 0

        if max_results_param:
            try:
                max_results_requested = int(max_results_param)
                if max_results_requested > self.get_max_results_allowed():
                    max_results = self.get_max_results_allowed()
                else:
                    max_results = max_results_requested
            except ValueError:
                max_results = self.get_default_max_results()
        else:
            max_results = self.get_default_max_results()

        return (start_index, max_results)

    def get_pagination_map(self, entries, pagination_params, total_count):
        return { 'start-index' : pagination_params[0],
                 'max-results' : pagination_params[1],
                 'total-results' : total_count,
                 'items' : entries }

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

    @staticmethod
    def get_prdict_user():
        """Examine the current user (based upon cookie), and return it,
        if found.  Otherwise, return None."""
        cookie_user = users.get_current_user()
        if not cookie_user:
            return None
        else:
            return prdict_user.lookup_user(cookie_user)

    def get_entry(self, key):
        try:
            return db.get(db.Key(encoded=key))
        except db.BadKeyError:
           return None

    def get_authorized_entry(self, key, access_mode):
        """Retrieve the entry in question from the datastore, and check
        permissions. If not found, render a 404 error view.
        If not permitted, render a 403 view.
        Otherwise, return the entry in question."""
        user = self.get_prdict_user()
        entry = self.get_entry(key)
        if access_mode == "read":
            content_type = self.get_read_content_type()
            if not entry:
                self.set_404(content_type, user)
                return
            if not self.is_user_authorized_to_read(user, entry):
                self.set_403(content_type, user)
                return None
        if access_mode == "write":
            content_type = self.get_write_content_type()
            if not entry:
                self.set_404(content_type, user)
                return
            if not self.is_user_authorized_to_write(user, entry):
                self.set_403(content_type, user)
                return None
        return entry

    def allow_overloaded_post_of_put_or_delete(self, key, content_type):
        """Lets a subclass handle overloaded POST of PUT or DELETE"""
        method_type = None
        if content_type == "json":
            parsed_json = json.loads(self.request.body)
            if "_method" in parsed_json:
                method_type = parsed_json["_method"]
        elif content_type == "form":
            method_type = self.request.get("_method")
        if method_type:
            if method_type == 'DELETE':
                return self.delete(key)
            elif method_type == 'PUT':
                return self.put(key)
        self.response.set_status(httplib.BAD_REQUEST)
        msg = "POST requires either '_method=DELETE' or '_method=PUT'"
        try:
            entry = db.get(db.Key(encoded = key))
        except db.BadKeyError:
            entry = None
        self.render_html(entry, msg)

    def allow_overloaded_post_of_delete(self, key, content_type):
        """Lets a subclass handle overloaded POST of DELETE"""
        if self.request.get('_method') == 'DELETE':
            return self.delete(key)
        self.response.set_status(httplib.BAD_REQUEST)
        msg = "POST requires '_method=DELETE'"
        try:
            entry = db.get(db.Key(encoded = key))
        except db.BadKeyError:
            entry = None
        self.render_html(entry, msg)

    def allow_overloaded_post_of_child_delete(self, parent_key, child_key):
        if self.request.get('_method') == "DELETE":
            return self.delete(parent_key, child_key)
        self.response.set_status(httplib.BAD_REQUEST)
        msg = "POST requires '_method=DELETE'"
        try:
            entry = db.get(db.Key(encoded = child_key))
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

    #delete this once all in svc layer
    def get_json_str(self, field_name):
        parsed_json = json.loads(self.request.body)
        if field_name in parsed_json:
            return parsed_json[field_name]
        else:
            return ""

    def _handle_pagination(self, parent, query):
        """Use request info to determine which children to return"""
        offset = 0
        start = self.request.get('start-index')
        if start:
            try:
                offset = int(start) - 1
            except ValueError:
                offset = None
            if offset is None or offset < 0:
                msg = "'start-index' parameter must be >= 1\n"
                self.response.set_status(httplib.BAD_REQUEST)
                self.set_header('Content-Type', 'text/plain; charset=UTF-8')
                self.write_message(msg)
                return (True, None, None, None)
        limit = self.DEFAULT_LIMIT
        nresults = self.request.get('max-results')
        if nresults:
            try:
                limit = min(self.DEFAULT_LIMIT, int(nresults))
            except ValueError:
                limit = None
            if limit is None or limit < 1:
                msg = "'max-results' parameter must be >= 1\n"
                self.response.set_status(httplib.BAD_REQUEST)
                self.set_header('Content-Type', 'text/plain; charset=UTF-8')
                self.write_message(msg)
                return (True, None, None, None)
        # the trick is: ask for one more row than you really want; if you
        # get the extra row then you know you need a next link
        entries = self.get_entries(parent, query, limit + 1, offset)
        
        # calculation of next and prev links
        prev_start, prev_max, next_start, next_max = \
                    self._calculate_page_indices(offset, limit, entries)
        prev_link = next_link = None
        if prev_start is not None:
            prev_link = "%s%s?start-index=%d&max-results=%d" % \
                        (self.baseurl(), self.request.path,
                         prev_start, prev_max)
        if next_start is not None:
            next_link = "%s%s?start-index=%d&max-results=%d" % \
                        (self.baseurl(), self.request.path,
                         next_start, next_max)
            
        if len(entries) > limit:
            # pare down to actual rows we want
            entries = entries[:limit]

        return (False, entries, prev_link, next_link)

    def render_json_ok(self):
        self.render_string(json.dumps({ 'status' : 'ok' }))
        
    def get_all_sports(self):
        query = db.GqlQuery("SELECT * FROM Sport ORDER BY title ASC")
        return query.fetch(100)

    def get_all_leagues(self):
        query = db.GqlQuery("SELECT * FROM League ORDER BY title ASC")
        return query.fetch(100)

    def get_all_teams(self):
        query = db.GqlQuery("SELECT * FROM Team ORDER BY title ASC")
        return query.fetch(1000)

    def get_all_events(self):
        event_query = db.GqlQuery("SELECT * FROM Event ORDER BY start_date ASC")
        return event_query.fetch(10000)

    def get_all_sportsevents(self):
        sportsevent_query = db.GqlQuery("SELECT * FROM SportsEvent ORDER BY start_date ASC")
        return sportsevent_query.fetch(10000)

    def get_all_game_kinds(self):
        return ["Regular Season", "Preseason", "Postseason"]

    @staticmethod
    def xml_escape(s):
        if s:
            return escape(s)
        else:
            return None

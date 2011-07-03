"""Abtract class for handling a request for a resource of a list of objects:
User's friends"""
import dateutil
import hashlib
import httplib
import logging
import simplejson as json

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from utils.constants import Constants
import build

class FeedHandler(AbstractHandler, BaseAuthorizationHandler):
    """Parent class for REST-based feed handlers.
    Feeds have 1 parent object and multiple contained entry objects"""
    DEFAULT_LIMIT = 75

    def __init__(self):
        self.html = "parent.html"
        self.entry_html = "entry.html"

    def get_entries(self, parent, limit = DEFAULT_LIMIT, offset = 0):
        """Returns the child entries of a parent,
        starting at offset and a max of limit."""
        raise Exception("Must be overridden by subclasses")

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        """Given a parent object and a list of entries related to the
        parent, render an HTML view.  If pagination links are provided,
        use them in the view."""
        raise Exception("Must be overridden by subclasses")

    def render_atom(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        """Given a parent object and a list of entries related to the
        parent, render an ATOM view.  If pagination links are provided,
        use them in the view."""
        raise Exception("Must be overridden by subclasses")

    def render_json(self, parent, entries):
        """Given a parent object and a list of entries related to the
        parent, render a JSON view.  If pagination links are provided,
        use them in the view."""
        parent_json = parent.to_json()
        entry_json = [json.loads(entry.to_json()) for entry in entries]
        self.render_string(json.dumps({ self.get_parent_name() :
                                        json.loads(parent_json),
                                        self.get_entries_name() :
                                        entry_json }))

    def get_parent_name(self):
        raise "Must be implemented by subclasses"

    def get_entries_name(self):
        raise "Must be implemented by subclasses"

    def render_entry_html(self, entry):
        """Given a created entry, render it to HTML."""
        raise Exception("Must be overridden by subclasses")

    @http_basic_auth
    def get(self, user, key):
        """Handles an HTTP GET by checking if user is authorized then
        returning parent/children according to HTTP request"""
        parent_entry = self.get_authorized_entry(key, "read")
        if not parent_entry:
            return
        (error_found, entries, prev_link, next_link) = \
                      self._handle_pagination(parent_entry)
        if error_found:
            return
        feed_etag = self._calculate_etag(parent_entry, entries)
        self.set_header("Etag", feed_etag)
        feed_lmdate = self._calculate_lmdate(parent_entry, entries)
        if feed_lmdate:
            self.set_header("Last-Modified", dateutil.http_header(feed_lmdate))
        self.set_header('Cache-Control', 'private, max-age=0')
        if not self.in_dev_mode() and \
           not self.modified(feed_etag, feed_lmdate):
            return self.response.set_status(httplib.NOT_MODIFIED)
        (content_type, vary) = self.get_read_content_type()
        if vary:
            self.set_header("Vary","Accept")
        if content_type == "atom":
            self.set_header("Content-Type", Constants.XML_ENCODING)
            self.render_atom(parent_entry, entries, prev_link, next_link)
            return
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(parent_entry, entries)
            return
        elif content_type == "html":
            self.render_html(parent_entry, entries, prev_link, next_link, None)
            return
        else:
            logging.error("Received a request type I can't handle %s" % request_type)

    @http_basic_auth
    def post(self, user, key):
        """Handles an HTTP POST by checking it is not overloaded PUT or DELETE,
        then checking if user is authorized, then validating new child and
        adding it to the resource."""
        content_type = self.get_write_content_type()
        if self.request.get('_method') == 'DELETE' or \
           self.request.get('_method') == 'PUT':
            self.response.set_status(httplib.BAD_REQUEST)
            msg = "Overloaded POST not allowed on this resource"
            try:
                parent = db.get(db.Key(encoded = key))
            except db.BadKeyError:
                parent = None
            self.set_400(self.html, content_type, user, msg)
            return
        parent_entry = self.get_authorized_entry(key, "write")
        if not parent_entry:
            return

        (is_content_type_ok, are_params_valid, is_db_write_ok,
         error_msg, new_entry) = self.create_entry(content_type)

        if not is_content_type_ok:
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template(self.html, { 'msg' : error_msg,
                                                     'current_user' : user,
                                                     'parent' : parent_entry })
        if not are_params_valid:
            return self.set_400(self.html, content_type, user, error_msg)

        if not is_db_write_ok:
            return self.handle_transient_error(content_type, user)

        self.handle_post_success(parent_entry, new_entry)
        entry_url = "%s/%s" % (self.request.url, new_entry.key())
        self.response.headers['Content-Location'] = entry_url
        self.response.set_status(httplib.CREATED)
        if content_type == "atom":
            raise "Not implemented yet"
        elif content_type == "json":
            self.set_header('Content-Type',
                            Constants.JSON_ENCODING)
            return self.render_json_ok()
        else:
            return self.render_template(self.entry_html, { 'entry' : new_entry,
                                                           'current_user' : user })

    def _handle_pagination(self, parent):
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
        entries = self.get_entries(parent, limit + 1, offset)

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

    @staticmethod
    def _calculate_page_indices(offset, limit, children):
        """Given offset and limit parameters, determine how to describe
        a next and previous page of children"""
        if offset > 0:
            prev_start = max(0, offset - limit) + 1
            prev_max = min(limit, offset)
        else:
            prev_start = prev_max = None
        if len(children) > limit:
            next_start = offset + limit + 1
            next_max = limit
        else:
            next_start = next_max = None
        return (prev_start, prev_max, next_start, next_max)

    @staticmethod
    def _calculate_etag(parent, entries):
        """ETag for feed is hash of (build number concatenated to parent key,
        parent etag, and all children key/etags)"""
        hasher = hashlib.md5()
        delimiter = ":"
        hasher.update(build.build_number)
        hasher.update(delimiter)
        hasher.update("%s%s%s" % (parent.key(), delimiter, parent.etag))
        hasher.update(delimiter)
        hasher.update(delimiter.join(["%s%s%s" %
                                      (entry.key(), delimiter, entry.etag)
                                      for entry in entries]))
        return ("W/\"%s\"" % hasher.hexdigest())

    @staticmethod
    def _calculate_lmdate( parent, entries):
        """No lm date for feed yet"""
        return None

    def write_message(self, msg):
        """Helper method for response writing"""
        self.response.out.write(msg)

    def create_entry(self, content_type):
        return self.get_svc().create_entry(self.request, content_type)

    #This is a hook for post-POST actions.  By default, do nothing
    def handle_post_success(self, parent_entry, new_entry):
        pass

    def get_svc(self):
        raise "Must be implemented by subclasses"

"""Abtract class for handling a request for a resource of a list of objects:
User's friends"""
import dateutil
import hashlib
import httplib
import logging

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from handlers.handler import AbstractHandler
from utils.constants import Constants
import build

class FeedHandler(AbstractHandler):
    """Parent class for REST-based feed handlers.
    Feeds have 1 parent object and multiple contained entry objects"""
    DEFAULT_LIMIT = 25

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

    def render_json(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        """Given a parent object and a list of entries related to the
        parent, render a JSON view.  If pagination links are provided,
        use them in the view."""
        raise Exception("Must be overridden by subclasses")

    def render_entry_html(self, entry):
        """Given a created entry, render it to HTML."""
        raise Exception("Must be overridden by subclasses")

    def get(self, key):
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
        request_type, vary = self.get_request_type()
        if vary:
            self.set_header("Vary","Accept")
        if request_type == "atom":
            self.set_header("Content-Type", "application/xml; charset=utf-8")
            self.render_atom(parent_entry, entries, prev_link, next_link)
            return
        if request_type == "json":
            self.set_header("Content-Type", "application/json; charset=utf-8")
            self.render_json(parent_entry, entries, prev_link, next_link)
            return
        if request_type == "html":
            self.render_html(parent_entry, entries, prev_link, next_link, None)
            return
        else:
            logging.error("Received a request tpye I can't handle %s" % request_type)
            
    def post(self, key):
        """Handles an HTTP POST by checking it is not overloaded PUT or DELETE,
        then checking if user is authorized, then validating new child and
        adding it to the resource."""
        if self.request.get('_method') == 'DELETE' or \
           self.request.get('_method') == 'PUT':
            self.response.set_status(httplib.BAD_REQUEST)
            msg = "Overloaded POST not allowed on this resource"
            try:
                parent = db.get(db.Key(encoded=key))
            except db.BadKeyError:
                parent = None
            self.render_html(parent, None, msg=msg)
            return
        parent_entry = self.get_authorized_entry(key, "write")
        if not parent_entry:
            return
        user = self.get_prdict_user()
        if not self.has_valid_data_media_type():
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            self.render_html(parent = parent_entry,
                             entries = None,
                             msg = "Must POST in %s format." % \
                             Constants.FORM_ENCODING)
            return
        (is_valid, error_message) = self.is_post_data_valid(parent_entry)
        if not is_valid:
            self.response.set_status(httplib.BAD_REQUEST)
            self.render_html(parent = parent_entry,
                             entries = self.get_entries(parent=parent_entry),
                             msg = error_message)
            return
        try:
            self.handle_post(parent_entry)
        except CapabilityDisabledError:
            self.handle_transient_error()
            return

    def is_post_data_valid(self):
        """Given data in the POST request, determine if it is valid.
        Return a (is_valid : Boolean, error_message : String) tuple."""
        raise Exception("Must be overridden by subclasses")

    def handle_post(self, parent_entry):
        """Given a parent in this feed, make the requested
        changes in the datastore and return an appropriate HTTP response."""
        raise Exception("Must be overridden in subclasses")

    def handle_newly_created_entry(self, created_entry):
        """Given a newly created entry, store it to the DB and
        return appropriate HTTP headers."""
        created_entry.put()
        created_entry_location = self.baseurl() + \
                                 created_entry.get_relative_url()
        self.response.set_status(httplib.CREATED)
        self.set_header('Content-Location', created_entry_location)
        self.render_entry_html(created_entry)

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

"""Abtract class for handling a request for a resource of a list of objects:
User's friends"""
from datetime import datetime
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
    DEFAULT_LIMIT = 1000

    def __init__(self):
        self.html = "parent.html"
        self.entry_html = "entry.html"

    def get_paginated_list(self, parent, pagination_params, query, sort):
        total_count = self.get_svc().get_count_by_parent(parent, query)
        entries = self.get_svc().get_entries_by_parent(parent, pagination_params, query, sort)
        return (total_count, entries)

    def render_atom(self, parent, entries, pagination_params):
        """Given a parent object and a list of entries related to the
        parent, render an ATOM view.  If pagination links are provided,
        use them in the view."""
        raise Exception("Not implemented yet")

    def render_json(self, parent, entries, pagination_params, total_count):
        """Given a parent object and a list of entries related to the
        parent, render a JSON view.  If pagination links are provided,
        use them in the view."""
        parent_json = parent.to_json()
        if entries and len(entries) > 0:
            json_entry_list = [json.loads(entry.to_json()) for entry in entries]
        else:
            json_entry_list = [ ]
        json_pagination_map = self.get_pagination_map(json_entry_list, pagination_params, total_count)
        self.render_string(json.dumps({ self.get_parent_name() :
                                        json.loads(parent_json),
                                        self.get_svc().get_entry_list_name() :
                                        json_pagination_map }))

    def get_parent_name(self):
        raise "Must be implemented by subclasses"

    def render_entry_html(self, entry):
        """Given a created entry, render it to HTML."""
        raise Exception("Must be overridden by subclasses")

    def get_sort_order(self):
        return None

    @http_basic_auth
    def get(self, user, key):
        """Handles an HTTP GET by checking if user is authorized then
        returning parent/children according to HTTP request"""
        parent_entry = self.get_authorized_entry(key, "read")
        if not parent_entry:
            return
        query = self.get_query()
        pagination_params = self.get_pagination_params()
        (total_count, entries) = self.get_paginated_list(parent_entry, pagination_params, query,
                                                         self.get_sort_order())
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
            self.render_atom(parent_entry, entries, pagination_params, total_count)
            return
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(parent_entry, entries, pagination_params, total_count)
            return
        elif content_type == "html":
            can_write = self.is_user_authorized_to_write(user, parent_entry)
            now = datetime.utcnow().strftime(AbstractHandler.DATE_FORMAT)
            param_map = { 'current_user' : user,
                          'can_write' : can_write,
                          'now' : now,
                          self.get_parent_name() : parent_entry,
                          self.get_svc().get_entry_list_name() : self.get_pagination_map(entries, pagination_params, total_count) }
            self.render_template(self.html, param_map)
            return
        else:
            logging.error("Received a content type I can't handle %s" % content_type)

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

    def get_max_results_allowed(self):
        raise "Must be implemented by subclasses"
    
    def get_default_max_results(self):
        raise "Must be implemented by subclasses"

    def get_svc(self):
        raise "Must be implemented by subclasses"

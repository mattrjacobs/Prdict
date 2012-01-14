"""Handles requests for the resource of all events"""
from datetime import datetime
import httplib
import logging
import simplejson as json

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from models import event
from models.abstract_model import AbstractModel
from utils.constants import Constants

class ListHandler(AbstractHandler, BaseAuthorizationHandler):
    """Handles requests for a list resource"""

    def __init__(self):
        self.html = "list.html"
        self.entry_html = "entry.html"

    def get_paginated_list(self, pagination_params, query):
        total_count = self.get_svc().get_count(query)
        entries = self.get_svc().get_entries(pagination_params, query)
        return (total_count, entries)

    @http_basic_auth
    def get(self, user):
        """Renders a list.
        If HTML, also renders a template for adding a new member, if the
        requesting user is an admin"""
        (content_type, vary) = self.get_read_content_type()
        query = self.get_query()
        pagination_params = self.get_pagination_params()
        (total_count, entries) = self.get_paginated_list(pagination_params, query)
        if vary:
            self.set_header("Vary", "Accept")
        if content_type == "atom":
            self.set_header("Content-Type", Constants.XML_ENCODING)
            self.render_atom(entries, pagination_params, total_count)
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(entries, pagination_params, total_count)
        else:
            can_write = self.is_user_authorized_to_write(user, None)
            now = datetime.utcnow().strftime(AbstractHandler.DATE_FORMAT)
            param_map = dict(self.create_param_map(user, entries, pagination_params, total_count,
                                                   can_write, now).items() +
                             self.get_extra_params().items())
            self.render_template(self.html, param_map)

    @http_basic_auth
    def post(self, user):
        """Attempts to respond to a POST by adding a new entry"""
        content_type = self.get_write_content_type()
        if not self.is_user_authorized_to_write(user, None):
            self.set_403(content_type, user)
            return None
        (is_content_type_ok, are_params_valid, is_db_write_ok,
         error_msg, new_entry) = self.create_entry(content_type)

        if not is_content_type_ok:
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template(self.html, { 'msg' : error_msg,
                                                     'current_user' : user})

        if not are_params_valid:
            return self.set_400(self.html, content_type, user, error_msg)

        if not is_db_write_ok:
            self.handle_transient_error(content_type, user)
            return

        entry_url = "%s/%s" % (self.request.url, new_entry.key())
        self.response.headers['Content-Location'] = entry_url
        self.response.set_status(httplib.CREATED)
        if content_type == "atom":
            raise "Not implemented yet"
        elif content_type == "json":
            self.set_header('Content-Type', Constants.JSON_ENCODING)
            return self.render_json_ok()
        else:
            return self.render_template(self.entry_html, { 'entry' : new_entry,
                                                           'current_user' : user})

    def render_json(self, entries, pagination_params, total_count):
        if entries and len(entries) > 0:
            json_entry_list = [json.loads(entry.to_json()) for entry in entries]
        else:
            json_entry_list = [ ]
        json_pagination_map = { self.get_svc().get_entry_list_name() : self.get_pagination_map(json_entry_list, pagination_params, total_count) }
        
        self.render_string(json.dumps(json_pagination_map))

    def render_atom(self):
        raise "Not implemented yet"

    def create_entry(self, content_type):
        return self.get_svc().create_entry(self.request, content_type)

    def get_sort_key(self):
        raise "Must be implemented by subclasses"

    def create_param_map(self, user, entries, pagination_params, total_count, can_write, now):
        return { 'current_user' : user,
                 'entries' : entries,
                 'start-index' : pagination_params[0],
                 'max-results' : pagination_params[1],
                 'total-results' : total_count,
                 'can_write' : can_write,
                 'now' : now }

    def get_extra_params(self):
        return {}

    def get_max_results_allowed(self):
        raise "Must be implemented by subclasses"

    def get_default_max_results(self):
        raise "Must be implemented by subclasses"

    def get_svc(self):
        raise "Must be implmented by subclasses"

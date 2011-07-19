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
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.html = "list.html"
        self.entry_html = "entry.html"

    @http_basic_auth
    def get(self, user):
        """Renders a list.
        If HTML, also renders a template for adding a new member, if the
        requesting user is an admin"""
        (content_type, vary) = self.get_read_content_type()
        query_param = self.request.get("q")
        query = None
        if query_param:
            if ":" in query_param:
                query = query_param.split(":", 2)
        if vary:
            self.set_header("Vary", "Accept")
        if content_type == "atom":
            self.set_header("Content-Type", Constants.XML_ENCODING)
            self.render_atom(query)
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(query)
        else:
            can_write = self.is_user_authorized_to_write(user, None)
            all_entries = self.get_all_entries(query)
            now = datetime.utcnow().strftime(ListHandler.DATE_FORMAT)
            param_map = self.create_param_map(user, all_entries, can_write, now)
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

    def render_json(self, query):
        all_entries = self.get_all_entries(query)
        if all_entries and len(all_entries) > 0:
            json_list = [json.loads(entry.to_json()) for entry in all_entries]
        else:
            json_list = [ ]
        self.render_string(json.dumps(json_list))

    def render_atom(self):
        raise "Not implemented yet"

    def create_entry(self, content_type):
        return self.get_svc().create_entry(self.request, content_type)

    def get_all_entries(self, query):
        if query:
            gql = db.GqlQuery("SELECT * FROM %s WHERE %s = :1 ORDER BY %s ASC" % (self.get_table_name(), query[0], self.get_sort_key()), query[1])
        else:
            gql = db.GqlQuery("SELECT * FROM %s ORDER BY %s ASC" % (self.get_table_name(), self.get_sort_key()))
        return gql.fetch(1000)
        
    def get_table_name(self):
        raise "Must be implemented by subclasses"

    def get_sort_key(self):
        raise "Must be implemented by subclasses"

    def create_param_map(self):
        raise "Must be implemented by subclasses"

    def get_svc(self):
        raise "Must be implmented by subclasses"

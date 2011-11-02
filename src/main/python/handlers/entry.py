"""Abstract class for handling single resources: Event/User"""
import dateutil
import httplib
import logging

from handlers.auth import http_basic_auth
from handlers.handler import AbstractHandler
from utils.constants import Constants

class EntryHandler(AbstractHandler):
    """Parent class for REST-based single-entity handlers."""

    def render_html(self, entry, msg=None):
        """Given a single entry, render an HTML view. Optionally also add
        the given message into the view if specified."""
        raise Exception("Must be overridden by subclasses")

    def render_atom(self, entry):
        """Given a single entry, render an ATOM view."""
        self.render_string(entry.to_xml())

    def render_json(self, entry):
        """Given a single entry, render a JSON view."""
        self.render_string(entry.to_json())

    @http_basic_auth
    def get(self, user, key):
        """Handles an HTTP GET by checking authorization and rendering
        the entry according to HTTP request, if authorized"""
        entry = self.get_authorized_entry(key, "read")
        if not entry:
            return
        self.handle_http_caching_headers(entry)
        self.handle_output(entry)

    def handle_http_caching_headers(self, entry):
        self.set_header('Etag', entry.etag)
        self.set_header('Last-Modified', dateutil.http_header(entry.updated))
        self.set_header('Cache-Control', 'private, max-age=0')
        if not self.in_dev_mode() and \
           not self.modified(entry.etag, entry.updated):
            return self.response.set_status(httplib.NOT_MODIFIED)

    def handle_output(self, entry):
        (content_type, vary) = self.get_read_content_type()
        if vary:
            self.set_header("Vary","Accept")
        if content_type == "atom":
            self.set_header("Content-Type", Constants.XML_ENCODING)
            self.render_atom(entry)
            return
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(entry)
            return
        elif content_type == "html":
            self.render_html(entry)
            return
        else:
            logging.error("Received a request type I can't handle : %s" % content_type)

    def post(self, key):
        """Handles an HTTP POST by only proceeding if it is an
        overloaded PUT or DELETE"""
        content_type = self.get_write_content_type()
        self.allow_overloaded_post_of_put_or_delete(key, content_type)

    @http_basic_auth
    def put(self, user, key):
        """Handles an HTTP PUT by checking if the user is authorized
        then doing the DB write and returning a representation of
        the new resource according to HTTP request"""
        entry_before_put = self.get_authorized_entry(key, "write")
        content_type = self.get_write_content_type()

        (is_content_type_ok, are_params_valid, preconditions_succeeded,
         db_lock_avoided, db_write_succeeded, error_msg, updated_entry) = \
         self.update_entry(entry_before_put, content_type)

        if not is_content_type_ok:
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template(self.get_html(entry_before_put),
                                        { 'msg' : error_msg,
                                          'current_user' : user })

        if not are_params_valid:
            return self.set_400(self.get_html(entry_before_put),
                                content_type, user, error_msg,
                                params = { "entry" : entry_before_put })

        if not preconditions_succeeded:
            self.response.set_status(httplib.PRECONDITION_FAILED)
            return self.render_template(self.get_html(entry_before_put),
                                        { 'msg' : error_msg,
                                          'current_user' : user })

        if not db_lock_avoided:
            self.response.set_status(httplib.CONFLICT)
            return self.render_template(self.get_html(entry_before_put),
                                        { 'msg' : error_msg,
                                          'current_user' : user })

        if not db_write_succeeded:
            self.response.set_status(httplib.SERVICE_UNAVAILABLE)
            return self.render_template(self.get_html(entry_before_put),
                                        { 'msg' : error_msg,
                                          'current_user' : user })

        self.response.set_status(httplib.OK)
        if content_type == "atom":
            raise "Not implemented yet"
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(updated_entry)
            return
        elif content_type == "form":
            self.render_html(updated_entry, "Entry updated")
            return
        else:
            logging.error("I don't know how to handle PUT of content type %s" % content_type)

    @http_basic_auth
    def delete(self, user, key):
        """Handles an HTTP DELETE by checking if the user is authorized
        then doing the DB delete"""
        entry_before_delete = self.get_authorized_entry(key, "write")
        (preconditions_succeeded, db_lock_avoided,
         db_write_succeeded, error_msg) = \
         self.delete_entry(entry_before_delete)

        if not preconditions_succeeded:
            self.response.set_status(httplib.PRECONDITION_FAILED)
            return self.render_template(self.get_html(entry_before_delete),
                                        { 'msg' : error_msg,
                                          'current_user' : user })
        if not db_lock_avoided:
            self.response.set_status(httplib.CONFLICT)
            return self.render.template(self.get_html(entry_before_delete),
                                        { 'msg' : error_msg,
                                          'current_user' : user })

        if not db_write_succeeded:
            self.response.set_status(httplib.SERVICE_UNAVAILABLE)
            return self.render.template(self.get_html(entry_before_delete),
                                        { 'msg' : error_msg,
                                          'current_user' : user })

        self.response.set_status(httplib.OK)
        content_type = self.get_write_content_type()
        if content_type == "atom":
            raise "Not implemented yet"
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            return self.render_json_ok()
        else:
            return self.render_html(None, "Entry deleted")
        
    def update_entry(self, entry, content_type):
        return self.get_svc().update_entry(entry, self.request, content_type)

    def delete_entry(self, entry):
        return self.get_svc().delete_entry(entry, self.request)

    def get_svc(self):
        raise "Must be implemented by subclasses"

    def get_html(self, entry):
        raise "Must be implemented by subclasses"

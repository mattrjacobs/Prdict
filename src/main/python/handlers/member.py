"""Abstract class for handling single resources: Event/User"""
import dateutil
import httplib
import logging

from handlers.handler import AbstractHandler
from utils.constants import Constants

class MemberHandler(AbstractHandler):
    """Parent class for REST-based handlers of single entities within a list."""

    def render_html(self, entry, msg=None):
        """Given a single entry, render an HTML view. Optionally also add
        the given message into the view if specified."""
        raise Exception("Must be overridden by subclasses")

    def render_atom(self, entry):
        """Given a single entry, render an ATOM view."""
        raise Exception("Must be overridden by subclasses")

    def render_json(self, entry):
        """Given a single entry, render a JSON view."""
        self.render_string(entry.to_json())

    def get(self, parent_key, child_key):
        """Handles an HTTP GET by checking authorization on the parent
        resource and rendering the child according to HTTP request,
        if authorized"""
        content_type = self.get_read_content_type()
        parent = self.get_authorized_entry(parent_key, "read")
        if not parent:
            return self.set_404(content_type)
        child = self.get_entry(child_key)
        if not child:
            return self.set_404(content_type)
        if not self.is_parent_of(parent, child):
            return self.set_404(content_type)
        self.handle_http_caching_headers(parent)
        self.handle_output(child)

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

    def post(self, parent_key, child_key):
        """Handles an HTTP POST by only proceeding if it is an
        overloaded DELETE"""
        self.allow_overloaded_post_of_child_delete(parent_key, child_key)

    def delete(self, parent_key, child_key):
        """Handles an HTTP DELETE by checking if the user is authorized
        then doing the DB delete of the member from the list"""
        self.response.set_status(httplib.METHOD_NOT_ALLOWED)

        # For the entities I'm working with, we never want to delete a
        # child's parent w/o updating it to something else.  So
        # the update call to the appropriate resource should work.
        #content_type = self.get_write_content_type()
        #parent = self.get_authorized_entry(parent_key, "write")
        #child = self.get_authorized_entry(child_key, "write")

        #if not parent or not child or not self.is_parent_of(parent, child):
        #    return self.set_404(content_type)

        #(preconditions_succeeded, db_lock_avoided,
        # db_write_succeeded, error_msg) = \
        # self.delete_child_from_parent(parent, child)

        #if not preconditions_succeeded:
        #    self.response.set_status(httplib.PRECONDITION_FAILED)
        #    return self.render_template(self.html, { 'msg' : error_msg,
        #                                             'current_user' : user })
        #if not db_lock_avoided:
        #    self.response.set_status(httplib.CONFLICT)
        #    return self.render.template(self.html, { 'msg' : error_msg,
        #                                             'current_user' : user })
        #if not db_write_succeeded:
        #    self.response.set_status(httplib.SERVICE_UNAVAILABLE)
        #    return self.render.template(self.html, { 'msg' : error_msg,
        #                                             'current_user' : user })

        #self.response.set_status(httplib.OK)
        #content_type = self.get_write_content_type()
        #if content_type == "atom":
        #    raise "Not implemented yet"
        #elif content_type == "json":
        #    self.set_header("Content-Type", Constants.JSON_ENCODING)
        #    return self.render_json_ok()
        #else:
        #    return self.render_html(None, "Entry deleted")
        
    def update_entry(self, entry, content_type):
        return self.get_svc().update_entry(entry, self.request, content_type)

    def delete_entry(self, entry):
        return self.get_svc().delete_entry(entry, self.request)

    def delete_child_from_parent(self, parent, child):
        return self.get_svc().delete_entry_from_parent(parent, child, self.request)

    def is_parent_of(self, parent, child):
        raise "Must be implemented by subclasses"

    def get_svc(self):
        raise "Must be implemented by subclasses"

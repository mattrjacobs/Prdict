"""Abstract class for handling single resources: Event/User"""
import cgi
import dateutil
import httplib
import logging

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from handlers.handler import AbstractHandler
from utils.constants import Constants

def put_txn(handler, entry):
    """Wraps a DB write triggered by HTTP PUT in txn"""
    if not entry:
        return (None, None, None)
    if not handler.precondition_passes(entry):
        status = httplib.PRECONDITION_FAILED
        msg = "Entry was out of date on update"
    else:
        status, msg = handler.update_entry(entry)
    if status == httplib.OK:
        entry.put()
    return entry, status, msg

def delete_txn(handler, entry):
    """Wraps a DB delete triggered by HTTP DELETE in txn"""
    if not entry:
        return (None, None, None)
    if not handler.precondition_passes(entry):
        return (entry, httplib.PRECONDITION_FAILED, "Entry was out-of-date.")
    entry.delete()
    return (None, httplib.OK, "Deleted.")

class EntryHandler(AbstractHandler):
    """Parent class for REST-based single-entity handlers."""

    def render_html(self, entry, msg=None):
        """Given a single entry, render an HTML view. Optionally also add
        the given message into the view if specified."""
        raise Exception("Must be overridden by subclasses")

    def render_atom(self, entry):
        """Given a single entry, render an ATOM view."""
        raise Exception("Must be overridden by subclasses")

    def render_json(self, entry):
        """Given a single entry, render a JSON view."""
        raise Exception("Must be overridden by subclasses")

    def get(self, key):
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
        request_type, vary = self.get_request_type()
        if vary:
            self.set_header("Vary","Accept")
        if request_type == "atom":
            self.set_header("Content-Type", "application/xml; charset=utf-8")
            self.render_atom(entry)
            return
        if request_type == "json":
            self.set_header("Content-Type", "application/json; charset=utf-8")
            self.render_json(entry)
            return
        if request_type == "html":
            self.render_html(entry)
            return
        else:
            logging.error("Received a request type I can't handle %s" % request_type)

    def post(self, key):
        """Handles an HTTP POST by only proceeding if it is an
        overloaded PUT or DELETE"""
        self.allow_overloaded_post_of_put_or_delete(key)

    def put(self, key):
        """Handles an HTTP PUT by checking if the user is authorized
        then doing the DB write and returning a representation of
        the new resource according to HTTP request""" 
        entry_before_put = self.get_authorized_entry(key, "write")
        try:
            entry, status, msg = \
                   db.run_in_transaction(put_txn, self, entry_before_put)
        except db.TransactionFailedError:
            entry = entry_before_put
            status = httplib.CONFLICT
            msg = "Update transaction failed."
        except CapabilityDisabledError:
            entry = entry_before_put
            status = httplib.SERVICE_UNAVAILABLE
            msg = "Unable to write data."
        if status is None:
            return
        if entry:
            self.response.set_status(status)
            request_type, _ = self.get_request_type()
            if request_type == "atom":
                self.set_header("Content-Type", 
                                "application/xml; charset=utf-8")
                self.render_atom(entry)
                return
            if request_type == "json":
                self.set_header("Content-Type",
                                "application/json; charset=utf-8")
                self.render_json(entry)
                return
            if request_type == "html":
                self.render_html(entry, msg)
                return
            else:
                logging.error("I don't know how to handle request type %s" % request_type)

    def delete(self, key):
        """Handles an HTTP DELETE by checking if the user is authorized
        then doing the DB delete"""
        entry_before_delete = self.get_authorized_entry(key, "write")
        try:
            entry, status, msg = \
                   db.run_in_transaction(delete_txn, self, entry_before_delete)
        except db.TransactionFailedError:
            entry = entry_before_delete
            status = httplib.CONFLICT
            msg = "Delete transaction failed."
        except CapabilityDisabledError:
            entry = entry_before_delete
            status = httplib.SERVICE_UNAVAILABLE
            msg = "Unable to write data."
        if status is None:
            return
        self.response.set_status(status)
        self.render_html(entry, msg)

    def update_entry(self, entry):
        """Given an entry, update it with the body of a PUT request,
        returning a pair of (status, msg) where status is the HTTP
        response code that resulted and msg is a string indicating
        further information (e.g. what syntax error caused a 400,
        for example."""
        if not self.has_valid_data_media_type():
            return (httplib.UNSUPPORTED_MEDIA_TYPE,
                    "Must provide body as %s" % Constants.FORM_ENCODING)
        params = cgi.parse_qs(self.request.body)
        return self._update_entry_from_params(entry, params)

    @staticmethod
    def _update_entry_from_params(entry, params):
        """Given an entry and params that might/might not be valid to
        construct an entry, update the entry with the param if possible.
        Return an (HTTP status, error_message) tuple."""
        raise Exception("Must be overridden by subclasses")

    def precondition_passes(self, entry):
        """All conditional clauses must pass on a conditional request,
        if multiple are specified (although this would be an odd thing
        for a client to do)."""
        if 'If-Match' in self.request.headers:
            req_etags = map(lambda s: s.strip(),
                            self.request.headers['If-Match'].split(','))
            if '*' in req_etags and entry is None:
                return False
            if entry.etag not in req_etags:
                return False
        if 'If-None-Match' in self.request.headers:
            req_etags = map(lambda s: s.strip(),
                            self.request.headers['If-None-Match'].split(','))
            if '*' in req_etags and entry is not None:
                return False
            if entry.etag in req_etags:
                return False
        if 'If-Unmodified-Since' in self.request.headers:
            req_lm = dateutil.parse_http_date(
                self.request.headers['If-Unmodified-Since'])
            if req_lm and dateutil.normalize(entry.updated) > req_lm:
                return False
        if 'If-Modified-Since' in self.request.headers:
            req_lm = dateutil.parse_http_date(
                self.request.headers['If-Modified-Since'])
            if req_lm and dateutil.normalize(entry.updated) <= req_lm:
                return False
        return True

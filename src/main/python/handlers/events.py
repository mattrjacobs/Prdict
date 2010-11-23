"""Handles requests for the resource of all events"""
from datetime import datetime
import httplib
import logging

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from auth import EventAuthorizationHandler
from handlers.handler import AbstractHandler
from models import event
from utils.constants import Constants

class EventsHandler(AbstractHandler, EventAuthorizationHandler):
    """Handles requests for the resource of all events."""
    def get(self):
        """Renders a template for adding a new event"""
        user = self.get_prdict_user()
        if not self.is_user_authorized_to_write(user, None):
            self.set_403()
            return None
        self.render_template('events.html')

    def post(self):
        """Attempts to respond to a POST by adding a new event"""
        user = self.get_prdict_user()
        if not self.is_user_authorized_to_write(user, None):
            self.set_403()
            return None
        if self.get_header('Content-Type') != Constants.FORM_ENCODING:
            msg = "Must POST in %s format." % Constants.FORM_ENCODING
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template('events.html', { 'msg': msg })
        title = self.request.get("title")
        description = self.request.get("description")
        start_date = self.request.get("start_date")
        end_date = self.request.get("end_date")
        (is_valid, error_message) = event.Event.validate_params(title, description, start_date, end_date)
        if not is_valid:
            return self.__bad_request_template(error_message)

        try:
            new_event = self.create_event(title, description, start_date, end_date)
        except CapabilityDisabledError:
            self.handle_transient_error()
            return
        event_url = "%s/%s" % (self.request.url, new_event.key())
        self.response.headers['Content-Location'] = event_url
        self.render_template('event.html', { 'event' : new_event })

    def create_event(self, title, description, start_date_str, end_date_str):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        new_event = event.Event(title = title, description = description,
                                start_date = start_date, end_date = end_date)
        new_event.put()
        self.response.set_status(httplib.CREATED)
        return new_event

    def __bad_request_template(self, message):
        """Returns an HTML template explaining why user add failed"""
        self.response.set_status(httplib.BAD_REQUEST)
        return self.render_template('events.html', { 'msg' : message })

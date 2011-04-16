"""Handles a request for an event"""
import httplib
import logging

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.event import Event
from services.event_svc import EventService

class EventHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an event resource.
    EntryHandler has logic for HTP operations
    EventAuthorizationHandler has logic for authorization."""
    def __init__(self):
        self.event_svc = EventService()

    def render_html(self, entry, msg=None):
        """Renders an HTML Event"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template(self.get_html(entry),
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'entry' : entry})

    def render_atom(self, entry):
        self.render_template("xml/%s_atom.xml" % entry.kind().lower(),
                             { 'entry' : entry, 'base_url' : self.baseurl() })

    def get_svc(self):
        return self.event_svc

    def get_html(self, entry):
        if entry:
            return "%s.html" % entry.kind().lower()
        else:
            return "event.html"

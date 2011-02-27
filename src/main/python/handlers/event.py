"""Handles a request for an event"""
import httplib

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.event import Event

class EventHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an event resource.
    EntryHandler has logic for HTP operations
    EventAuthorizationHandler has logic for authorization."""
    def render_html(self, entry, msg=None):
        """Renders an HTML Event"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("event.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'event' : entry})

    def render_atom(self, entry):
        self.render_template('xml/event_atom.xml',
                             { 'event' : entry, 'base_url' : self.baseurl() })

    def render_json(self, entry):
        self.render_template('json/event_json.json',
                             { 'event' : entry })

    @staticmethod
    def _update_entry_from_params(event, params):
        """Given a dict of params, update an event resource if they are valid."""
        messages = []
        title_valid = desc_valid = start_date_valid = end_date_valid = True
        
        if 'title' in params:
            title = params['title'][0]
            (title_valid, msg) = Event.validate_title(title)
            if not title_valid:
                messages.append(msg)

        if 'description' in params:
            description = params['description'][0]
            (desc_valid, msg) = Event.validate_description(description)
            if not desc_valid:
                messages.append(msg)

        if 'start_date' in params:
            start_date = params['start_date'][0]
            (start_date_valid, msg) = Event.validate_start_date(start_date)
            if not start_date_valid:
                messages.append(msg)

        if 'end_date' in params:
            end_date = params['end_date'][0]
            (end_date_valid, msg) = Event.validate_end_date(end_date)
            if not end_date_valid:
                messages.append(msg)

        if title_valid and desc_valid and start_date_valid and end_date_valid:
            if title:
                event.title = title
            if description:
                event.description = description
            if start_date:
                event.start_date = Event.convert_date_format(start_date)
            if end_date:
                event.end_date = Event.convert_date_format(end_date)

            return (httplib.OK, "Event updated.")
        else:
            return (httplib.BAD_REQUEST, ','.join(messages))


"""Handles a request for a sport"""
import httplib

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.sport import Sport

class SportHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an sport resource.
    EntryHandler has logic for HTTP operations
    BaseAuthorizationHandler has logic for authorization."""
    def render_html(self, entry, msg=None):
        """Renders an HTML Sport"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("sport.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'sport' : entry})

    def render_atom(self, league):
        self.render_template('xml/sport_atom.xml',
                             { 'sport' : entry, 'base_url' : self.baseurl() })

    def render_json(self, entry):
        self.render_template('json/sport_json.json',
                             { 'sport' : entry })

    @staticmethod
    def _update_entry_from_params(sport, params):
        """Given a dict of params, update a sport resource if they are valid."""
        messages = []
        title_valid = desc_valid = True
        
        if 'title' in params:
            title = params['title'][0]
            (title_valid, msg) = Sport.validate_title(title)
            if not title_valid:
                messages.append(msg)

        if 'description' in params:
            description = params['description'][0]
            (desc_valid, msg) = Sport.validate_description(description)
            if not desc_valid:
                messages.append(msg)

        if title_valid and desc_valid:
            if title:
                sport.title = title
            if description:
                sport.description = description

            return (httplib.OK, "Sport updated.")
        else:
            return (httplib.BAD_REQUEST, ','.join(messages))


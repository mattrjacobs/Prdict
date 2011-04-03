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
                               'item' : entry})

    def render_atom(self, league):
        self.render_template('xml/sport_atom.xml',
                             { 'item' : entry, 'base_url' : self.baseurl() })

    def render_json(self, entry):
        self.render_template('json/sport_json.json',
                             { 'item' : entry })

    def parse_put_params(self, params):
        parsed_params = dict()
        messages = []
        title_valid = desc_valid = True
        
        if 'title' in params:
            title = params['title'][0]
            (title_valid, msg) = Sport.validate_title(title)
            if not title_valid:
                messages.append(msg)
            else:
                parsed_params['title'] = title

        if 'description' in params:
            description = params['description'][0]
            (desc_valid, msg) = Sport.validate_description(description)
            if not desc_valid:
                messages.append(msg)
            else:
                parsed_params['description'] = description

        return (title_valid and desc_valid, messages, parsed_params)

    def update_entry(self, sport, parsed_params):
        if 'title' in parsed_params:
            sport.title = parsed_params['title']
        if 'description' in parsed_params:
            sport.description = parsed_params['description']
        return (httplib.OK, "Sport updated.")


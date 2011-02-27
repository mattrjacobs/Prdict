"""Handles a request for a league"""
import httplib

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.league import League

class LeagueHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an league resource.
    EntryHandler has logic for HTTP operations
    LeagueAuthorizationHandler has logic for authorization."""
    def render_html(self, entry, msg=None):
        """Renders an HTML Event"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("league.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'item' : entry})

    def render_atom(self, league):
        self.render_template('xml/league_atom.xml',
                             { 'item' : entry, 'base_url' : self.baseurl() })

    def render_json(self, entry):
        self.render_template('json/league_json.json',
                             { 'item' : entry })

    @staticmethod
    def _update_entry_from_params(league, params):
        """Given a dict of params, update a league resource if they are valid."""
        messages = []
        title_valid = desc_valid = True
        
        if 'title' in params:
            title = params['title'][0]
            (title_valid, msg) = League.validate_title(title)
            if not title_valid:
                messages.append(msg)

        if 'description' in params:
            description = params['description'][0]
            (desc_valid, msg) = League.validate_description(description)
            if not desc_valid:
                messages.append(msg)

        if title_valid and desc_valid:
            if title:
                league.title = title
            if description:
                league.description = description

            return (httplib.OK, "League updated.")
        else:
            return (httplib.BAD_REQUEST, ','.join(messages))


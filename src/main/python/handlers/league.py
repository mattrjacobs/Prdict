"""Handles a request for a league"""
import httplib
import logging

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.league import League
from models.sport import Sport

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
                               'item' : entry,
                               'sports' : self.get_all_sports() })

    def render_atom(self, league):
        self.render_template('xml/league_atom.xml',
                             { 'item' : entry, 'base_url' : self.baseurl() })

    def render_json(self, entry):
        self.render_template('json/league_json.json',
                             { 'item' : entry })

    def parse_put_params(self, params):
        parsed_params = dict()
        messages = []
        title_valid = desc_valid = sport_valid = True
        
        if 'title' in params:
            title = params['title'][0]
            (title_valid, msg) = League.validate_title(title)
            if not title_valid:
                messages.append(msg)
            else:
                parsed_params['title'] = title

        if 'description' in params:
            description = params['description'][0]
            (desc_valid, msg) = League.validate_description(description)
            if not desc_valid:
                messages.append(msg)
            else:
                parsed_params['description'] = description

        if 'sport' in params:
            sport_param = params['sport'][0]
            sport = Sport.find_by_name(sport_param)
            if not sport:
                sport_valid = False
                messages.append("Could not find sport named %s" % sport_param)
            else:
                parsed_params['sport'] = sport

        return (title_valid and desc_valid and sport_valid,
                messages, parsed_params)

    def update_entry(self, league, parsed_params):
        """Given a dict of known good params, update the league resource"""
        if 'title' in parsed_params:
            league.title = parsed_params['title']

        if 'description' in parsed_params:
            league.description = parsed_params['description']

        if 'sport' in parsed_params:
            sport = parsed_params['sport']
            league.sport = sport

        return (httplib.OK, "League updated.")

"""Handles a request for a team"""
import httplib
import logging

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.league import League
from models.team import Team

class TeamHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an team resource.
    EntryHandler has logic for HTTP operations
    LeagueAuthorizationHandler has logic for authorization."""
    def render_html(self, entry, msg=None):
        """Renders an HTML Team"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("team.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'item' : entry,
                               'leagues' : self.get_all_leagues() })

    def render_atom(self, team):
        self.render_template('xml/team_atom.xml',
                             { 'item' : entry, 'base_url' : self.baseurl() })

    def render_json(self, entry):
        self.render_template('json/team_json.json',
                             { 'item' : entry })

    def parse_put_params(self, params):
        parsed_params = dict()
        messages = []
        title_valid = desc_valid = league_valid = location_valid = True
        
        if 'title' in params:
            title = params['title'][0]
            (title_valid, msg) = Team.validate_title(title)
            if not title_valid:
                messages.append(msg)
            else:
                parsed_params['title'] = title

        if 'description' in params:
            description = params['description'][0]
            (desc_valid, msg) = Team.validate_description(description)
            if not desc_valid:
                messages.append(msg)
            else:
                parsed_params['description'] = description

        if 'location' in params:
            location = params['location'][0]
            (location_valid, msg) = Team.validate_location(location)
            if not location_valid:
                messages.append(msg)
            else:
                parsed_params['location'] = location

        if 'league' in params:
            league_param = params['league'][0]
            league = League.find_by_name(league_param)
            if not league:
                league_valid = False
                messages.append("Could not find league named %s" % league_param)
            else:
                parsed_params['league'] = league

        return (title_valid and desc_valid and league_valid and location_valid,
                messages, parsed_params)

    def update_entry(self, team, parsed_params):
        """Given a dict of known good params, update the team resource"""
        if 'title' in parsed_params:
            team.title = parsed_params['title']

        if 'description' in parsed_params:
            team.description = parsed_params['description']

        if 'location' in parsed_params:
            team.location = parsed_params['location']

        if 'league' in parsed_params:
            league = parsed_params['league']
            team.league = league

        return (httplib.OK, "Team updated.")

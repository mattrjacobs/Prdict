"""Handles requests for the resource of all leagues"""
from google.appengine.ext import db

import logging

from handlers.list import ListHandler
from models.league import League
from models.team import Team

class TeamsHandler(ListHandler):
    """Handles requests for the resource of all teams."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "teams.html"
        self.item_html = "team.html"

    def get_all_items(self):
        return self.get_all_teams()

    def validate_other_params(self):
        league_param = self.request.get('league')
        if league_param:
            league = League.find_by_name(league_param)
            if not league:
                return (False, "Could not find league named %s" % league_param)
        else:
            return (False, "No league set")
        location_param = self.request.get('location')
        if location_param:
            location = location_param
        else:
            return (False, "No location set")
        return (True, None)

    def create_params(self, title, description):
        league_param = self.request.get('league')
        league = League.find_by_name(league_param)
        location = self.request.get('location')
        return (title, description, league, location)

    def instantiate_new_item(self, params):
        (title, description, league, location) = params
        new_team = Team(title = title, description = description, league = league, location = location)
        return new_team

    def create_param_map(self, user, all_items, can_write, now):
        param_map = { 'current_user' : user, 'items' : all_items,
                      'can_write' : can_write, 'now' : now,
                      'leagues' : self.get_all_leagues() }
        return param_map

"""Handles requests for the resource of all leagues"""
from google.appengine.ext import db

import logging

from handlers.list import ListHandler
from models.league import League
from models.sport import Sport

class LeaguesHandler(ListHandler):
    """Handles requests for the resource of all leagues."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "leagues.html"
        self.item_html = "league.html"

    def get_all_items(self):
        return self.get_all_leagues()

    def validate_other_params(self):
        sport_param = self.request.get('sport')
        if sport_param:
            sport = Sport.find_by_name(sport_param)
            if sport:
                return (True, None)
            else:
                return (False, "Could not find sport named %s" % sport_param)
        else:
            return (False, "Needs a 'sport' parameter")

    def create_params(self, title, description):
        sport_param = self.request.get('sport')
        sport = Sport.find_by_name(sport_param)
        return (title, description, sport)

    def instantiate_new_item(self, params):
        (title, description, sport) = params
        new_league = League(title = title, description = description, sport = sport)
        return new_league

    def create_param_map(self, user, all_items, can_write, now):
        param_map = { 'current_user' : user, 'items' : all_items,
                      'can_write' : can_write, 'now' : now,
                      'sports' : self.get_all_sports() }
        return param_map

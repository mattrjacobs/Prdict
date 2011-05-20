"""Handles requests for the resource of all leagues"""
import logging
import simplejson as json

from handlers.list import ListHandler
from services.league_svc import LeagueService

class LeaguesHandler(ListHandler):
    """Handles requests for the resource of all leagues."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "leagues.html"
        self.entry_html = "league.html"
        self.league_svc = LeagueService()

    def create_param_map(self, user, all_entries, can_write, now):
        param_map = { 'current_user' : user, 'entries' : all_entries,
                      'can_write' : can_write, 'now' : now,
                      'sports' : self.get_all_sports() }
        return param_map

    def get_table_name(self):
        return "League"

    def get_sort_key(self):
        return "title"

    def get_svc(self):
        return self.league_svc

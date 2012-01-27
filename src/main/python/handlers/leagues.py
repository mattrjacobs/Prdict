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

    def get_extra_params(self):
        return { 'sports' : self.get_all_sports() }

    def get_sort_order(self):
        return "title"

    def get_max_results_allowed(self):
        return 200
    
    def get_default_max_results(self):
        return 25

    def get_sort_key(self):
        return "title"

    def get_svc(self):
        return LeagueService()

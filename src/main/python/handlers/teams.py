"""Handles requests for the resource of all leagues"""
import logging

from handlers.list import ListHandler
from services.team_svc import TeamService

class TeamsHandler(ListHandler):
    """Handles requests for the resource of all teams."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "teams.html"
        self.entry_html = "team.html"

    def get_extra_params(self):
        return {'leagues' : self.get_all_leagues()}

    def get_max_results_allowed(self):
        return 500

    def get_default_max_results(self):
        return 100

    def get_sort_key(self):
        return "title"

    def get_svc(self):
        return TeamService()

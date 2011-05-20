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
        self.team_svc = TeamService()

    def create_param_map(self, user, all_entries, can_write, now):
        param_map = { 'current_user' : user, 'entries' : all_entries,
                      'can_write' : can_write, 'now' : now,
                      'leagues' : self.get_all_leagues() }
        return param_map

    def get_table_name(self):
        return "Team"

    def get_sort_key(self):
        return "title"

    def get_svc(self):
        return self.team_svc

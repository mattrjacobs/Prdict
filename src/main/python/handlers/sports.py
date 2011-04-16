"""Handles requests for the resource of all sports"""
from google.appengine.ext import db

from handlers.list import ListHandler
from services.sport_svc import SportService

class SportsHandler(ListHandler):
    """Handles requests for the resource of all sports."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "sports.html"
        self.entry_html = "sport.html"
        self.sport_svc = SportService()

    def get_all_entries(self):
        return self.get_all_sports()

    def create_param_map(self, user, all_entries, can_write, now):
        param_map = { 'current_user' : user, 'entries' : all_entries,
                      'can_write' : can_write, 'now' : now }
        return param_map

    def get_svc(self):
        return self.sport_svc

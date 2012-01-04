"""Handles requests for the resource of all sports"""
from handlers.list import ListHandler
from services.sport_svc import SportService

class SportsHandler(ListHandler):
    """Handles requests for the resource of all sports."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "sports.html"
        self.entry_html = "sport.html"

    def get_max_results_allowed(self):
        return 100

    def get_default_max_results(self):
        return 25

    def get_sort_key(self):
        return "title"

    def get_svc(self):
        return SportService()

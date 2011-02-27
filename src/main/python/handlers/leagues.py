"""Handles requests for the resource of all leagues"""
from google.appengine.ext import db

from handlers.list import ListHandler
from models import league

class LeaguesHandler(ListHandler):
    """Handles requests for the resource of all leagues."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "leagues.html"
        self.item_html = "league.html"

    def get_all_items(self):
        query = db.GqlQuery("SELECT * FROM League")
        return query.fetch(100)

    def create_params(self, title, description):
        return (title, description)

    def instantiate_new_item(self, params):
        (title, description) = params
        new_league = league.League(title = title, description = description)
        return new_league

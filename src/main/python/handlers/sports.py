"""Handles requests for the resource of all sports"""
from google.appengine.ext import db

from handlers.list import ListHandler
from models import sport

class SportsHandler(ListHandler):
    """Handles requests for the resource of all sports."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "sports.html"
        self.item_html = "sport.html"

    def get_all_items(self):
        query = db.GqlQuery("SELECT * FROM Sport")
        return query.fetch(100)

    def create_params(self, title, description):
        return (title, description)

    def instantiate_new_item(self, params):
        (title, description) = params
        new_sport = sport.Sport(title = title, description = description)
        return new_sport

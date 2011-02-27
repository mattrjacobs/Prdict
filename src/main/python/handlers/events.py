"""Handles requests for the resource of all events"""
from datetime import datetime
import logging

from google.appengine.ext import db

from handlers.list import ListHandler
from models import event

class EventsHandler(ListHandler):
    """Handles requests for the resource of all events."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "events.html"
        self.item_html = "event.html"

    def get_all_items(self):
        query = db.GqlQuery("SELECT * FROM Event")
        return query.fetch(100)

    def validate_other_params(self):
        start_date = self.request.get("start_date")
        end_date = self.request.get("end_date")
        return event.Event.validate_dates(start_date, end_date)

    def create_params(self, title, description):
        start_date_str = self.request.get("start_date")
        end_date_str = self.request.get("end_date")
        start_date = datetime.strptime(start_date_str, ListHandler.DATE_FORMAT)
        end_date = datetime.strptime(end_date_str, ListHandler.DATE_FORMAT)
        return (title, description, start_date, end_date)

    def instantiate_new_item(self, params):
        (title, description, start_date, end_date) = params
        new_event = event.Event(title = title, description = description,
                                start_date = start_date, end_date = end_date)
        return new_event

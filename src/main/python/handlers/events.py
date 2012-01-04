"""Handles requests for the resource of all events"""
from datetime import datetime
import logging

from handlers.list import ListHandler
from models import event
from services.event_svc import EventService

class EventsHandler(ListHandler):
    """Handles requests for the resource of all events."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "events.html"
        self.entry_html = "event.html"

    def get_extra_params(self):
        return {'leagues' : self.get_all_leagues(),
                'game_kinds' : self.get_all_game_kinds() }

    def get_max_results_allowed(self):
        return 200

    def get_default_max_results(self):
        return 25

    def get_sort_key(self):
        return "start_date"

    def create_entry(self, content_type):
        return self.get_svc().create_entry(self.request, content_type)

    def get_svc(self):
        return EventService()

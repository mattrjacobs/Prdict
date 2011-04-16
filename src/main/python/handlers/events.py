"""Handles requests for the resource of all events"""
from datetime import datetime
import logging

from google.appengine.ext import db

from handlers.list import ListHandler
from models import event
from services.event_svc import EventService

class EventsHandler(ListHandler):
    """Handles requests for the resource of all events."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "events.html"
        self.entry_html = "event.html"
        self.svc = EventService()

    def get_all_entries(self):
        return self.get_all_sportsevents()

    def create_param_map(self, user, all_entries, can_write, now):
        all_leagues = self.get_all_leagues()
        return { 'current_user' : user, 'entries' : all_entries,
                 'can_write' : can_write, 'now' : now,
                 'leagues' : self.get_all_leagues(),
                 'game_kinds' : self.get_all_game_kinds() }

    def create_entry(self, content_type):
        return self.svc.create_entry(self.request, content_type)


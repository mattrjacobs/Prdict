"""Handles requests for a list of events"""
from datetime import datetime
import logging

from handlers.list import ListHandler
from models import event
from services.event_svc import EventService

class EventListHandler(ListHandler):
    """Handles requests for a list of events."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "readonly_events.html"

    def get_query(self):
        league_query_param = self.request.get("league")
        team_query_param = self.request.get("team")
        queries = []
        if league_query_param:
            queries.append(("league", league_query_param))
        if team_query_param:
            queries.append(("team", team_query_param))
        return queries

    def get_paginated_list(self, pagination_params, query, sort):
        raise "Must be implemented by subclasses"

    def get_max_results_allowed(self):
        return 100

    def get_default_max_results(self):
        return 10

    def post(self, user):
        self.set_status(httplib.METHOD_NOT_IMPLEMENTED)
        return

    def get_svc(self):
        return EventService()

"""Handles requests for the resource of all recent events"""
from datetime import datetime
import logging

from handlers.list import ListHandler
from models import event
from services.event_svc import EventService

class RecentEventsHandler(ListHandler):
    """Handles requests for the resource of all recent events."""
    def __init__(self):
        ListHandler.__init__(self)
        self.html = "readonly_events.html"

    def get_query(self):
        query_param = self.request.get("league")
        if query_param:
            return ["league", query_param]
        return None
        
    def get_paginated_list(self, pagination_params, query, sort):
        total_count = self.get_svc().get_count_of_recent_events(query)
        entries = self.get_svc().get_recent_events(pagination_params, query)
        return (total_count, entries)

    def get_max_results_allowed(self):
        return 100

    def get_default_max_results(self):
        return 10

    def post(self, user):
        self.set_status(httplib.METHOD_NOT_IMPLEMENTED)
        return

    def get_svc(self):
        return EventService()

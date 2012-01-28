import logging

from handlers.events_list import EventListHandler

class RecentEventsHandler(EventListHandler):
    def get_paginated_list(self, pagination_params, query, sort):
        total_count = self.get_svc().get_count_of_recent_events(query)
        entries = self.get_svc().get_recent_events(pagination_params, query)
        return (total_count, entries)

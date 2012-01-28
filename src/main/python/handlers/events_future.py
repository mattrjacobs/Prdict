import logging

from handlers.events_list import EventListHandler

class FutureEventsHandler(EventListHandler):
    def get_paginated_list(self, pagination_params, query, sort):
        total_count = self.get_svc().get_count_of_future_events(query)
        entries = self.get_svc().get_future_events(pagination_params, query)
        return (total_count, entries)

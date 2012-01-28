import logging

from handlers.events_list import EventListHandler

class InProgressEventsHandler(EventListHandler):
    def get_paginated_list(self, pagination_params, query, sort):
        total_count = self.get_svc().get_count_of_inprogress_events(query)
        entries = self.get_svc().get_inprogress_events(pagination_params, query)
        return (total_count, entries)

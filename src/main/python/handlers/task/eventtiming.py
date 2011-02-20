from handlers.handler import AbstractHandler

from datetime import datetime
import logging

from google.appengine.api import memcache
from google.appengine.ext import db

from models import prdict_user
from models.event import Event

class EventTimingTaskHandler(AbstractHandler):
    CRON_HEADER = "X-AppEngine-Cron"

    def get_top_friends(self, user, num):
        return [prdict_user.lookup_user(u) for u in user.friends[0 : num]] 

    def get_past_events(self, num):
        query = db.GqlQuery("SELECT * FROM Event WHERE end_date < :1 ORDER BY end_date DESC", datetime.now())
        return query.fetch(num, 0)

    def get_current_events(self, num):
        end_in_future_query = db.GqlQuery("SELECT * FROM Event WHERE end_date > :1 ORDER BY end_date ASC", datetime.now())
        start_in_past_query = db.GqlQuery("SELECT * FROM Event WHERE start_date < :1 ORDER BY start_date DESC", datetime.now())
        end_in_future = end_in_future_query.fetch(num * 2, 0)
        start_in_past = start_in_past_query.fetch(num * 2, 0)
        current_events = []
        for event in end_in_future:
            if str(event.key()) in map(lambda event: str(event.key()), start_in_past):
                current_events.append(event)
        return current_events

    def get_next_events(self, num):
        query = db.GqlQuery("SELECT * FROM Event WHERE start_date > :1 ORDER BY start_date ASC", datetime.now())
        return query.fetch(num, 0)

    # used for cron
    def get(self):
        if self.is_dev_host() or self.is_cron_request():
            self.handle_recalc()

    # used for task queue
    def post(self):
        logging.error("Shouldn't be receiving a POST here")
        #self.handle_recalc()

    def handle_recalc(self):
        past_events = self.get_past_events(10)
        current_events = self.get_current_events(10)
        next_events = self.get_next_events(10)

        event_timing = { 'past' : past_events,
                         'current' : current_events,
                         'future' : next_events }

        memcache.set('event_timing', event_timing)

    def is_cron_request(self):
        hdr = self.get_header(EventTimingTaskHandler.CRON_HEADER)
        if hdr:
            return hdr.lower() == "true"
        else:
            return False

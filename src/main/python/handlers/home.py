from handlers.handler import AbstractHandler

import datetime
import logging

from google.appengine.api import memcache
from google.appengine.ext import db

from auth import http_basic_auth
from models import prdict_user

class HomeHandler(AbstractHandler):
    def get_top_friends(self, user, num):
        return [prdict_user.lookup_user(u) for u in user.friends[0 : num]] 

    @http_basic_auth
    def get(self, user):
        if user:
            top_friends = self.get_top_friends(user, 10)
        else:
            top_friends = []

        #event_timings = memcache.get('event_timing')
        #if event_timings:
        #    past_events = event_timings['past']
        #    current_events = event_timings['current']
        #    future_events = event_timings['future']
        #else:
        #    past_events = []
        #    current_events = []
        #    future_events = []

        

        
        self.render_template("home.html",
                             { 'current_user' : user,
                               'top_friends' : top_friends,
                               'past_events' : self.get_past_events(10),
                               'current_events' : self.get_current_events(10),
                               'future_events' : self.get_next_events(10) })

    def get_past_events(self, num):
        start = datetime.datetime.utcnow()
        query = db.GqlQuery("SELECT * FROM SportsEvent WHERE end_date < :1 ORDER BY end_date DESC", datetime.datetime.utcnow())
        end = datetime.datetime.utcnow()
        woo = query.fetch(num, 0)
        logging.error("PAST EVENTS : %s" % (end - start))
        return woo
    
    def get_current_events(self, num):
        start = datetime.datetime.utcnow()
        end_in_future_query = db.GqlQuery("SELECT * FROM SportsEvent WHERE end_date > :1 ORDER BY end_date ASC", datetime.datetime.utcnow())
        start_in_past_query = db.GqlQuery("SELECT * FROM SportsEvent WHERE start_date < :1 ORDER BY start_date DESC", datetime.datetime.utcnow())
        end_in_future = end_in_future_query.fetch(num * 2, 0)
        start_in_past = start_in_past_query.fetch(num * 2, 0)
        current_events = []
        for event in end_in_future:
            if str(event.key()) in map(lambda event: str(event.key()), start_in_past):
                current_events.append(event)
        end = datetime.datetime.utcnow()
        logging.error("CURRENT : %s" % (end - start))
        return current_events
            
    def get_next_events(self, num):
        start = datetime.datetime.utcnow()
        query = db.GqlQuery("SELECT * FROM SportsEvent WHERE start_date > :1 ORDER BY start_date ASC", datetime.datetime.utcnow())
        woo = query.fetch(num, 0)
        end = datetime.datetime.utcnow()
        logging.error("NEXT : %s" % (end - start))
        return woo

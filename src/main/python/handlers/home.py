from handlers.handler import AbstractHandler

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

        event_timings = memcache.get('event_timing')
        if event_timings:
            past_events = event_timings['past']
            current_events = event_timings['current']
            future_events = event_timings['future']
        else:
            past_events = []
            current_events = []
            future_events = []
        
        self.render_template("home.html",
                             { 'current_user' : user,
                               'top_friends' : top_friends,
                               'past_events' : past_events,
                               'current_events' : current_events,
                               'future_events' : future_events })

from handlers.handler import AbstractHandler

from datetime import datetime
import logging

from google.appengine.ext import db

from models import prdict_user

class HomeHandler(AbstractHandler):
    def get_top_friends(self, user, num):
        return [prdict_user.lookup_user(u) for u in user.friends[0:num]] 

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

    def get(self):
        current_user = self.get_prdict_user()
        if current_user:
            top_friends = self.get_top_friends(current_user, 10)
        else:
            top_friends = []
        past_events = self.get_past_events(10)
        current_events = self.get_current_events(10)
        next_events = self.get_next_events(10)
        
        self.render_template("home.html",
                             { 'current_user' : current_user,
                               'top_friends' : top_friends,
                               'past_events' : past_events,
                               'current_events' : current_events,
                               'next_events' : next_events })

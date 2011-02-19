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
        dummy_query = db.GqlQuery("SELECT * FROM Event")
        for event in dummy_query.fetch(100, 0):
            logging.error("EVENT NAME : %s" % event.title)
            logging.error("DATE RANGE : %s" % event.date_range)
            #logging.error("START : %s" % (event.date_range > datetime.now()))
            #logging.error("END : %s" % (event.date_range < datetime.now()))

        dummy_end_query = db.GqlQuery("SELECT * FROM Event WHERE date_range > :1", datetime.now())
        for event in dummy_end_query.fetch(100, 0):
            logging.error("END EVENT NAME : %s" % event.title)
            logging.error("END DATE RANGE : %s" % event.date_range)

        dummy_start_query = db.GqlQuery("SELECT * FROM Event WHERE date_range < :1", datetime.now())
        for event in dummy_start_query.fetch(100, 0):
            logging.error("START EVENT NAME : %s" % event.title)
            logging.error("START DATE RANGE : %s" % event.date_range)

        query = db.GqlQuery("SELECT * FROM Event WHERE date_range > :1 AND date_range < :1", datetime.now())
        return query.fetch(10, 0)

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

        logging.error("CURRENT EVENTS : %s" % str(current_events))
        
        self.render_template("home.html",
                             { 'current_user' : current_user,
                               'top_friends' : top_friends,
                               'past_events' : past_events,
                               'current_events' : current_events,
                               'next_events' : next_events })

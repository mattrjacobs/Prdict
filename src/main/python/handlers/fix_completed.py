from handlers.handler import AbstractHandler

import logging

from google.appengine.ext import db

class FixCompletedHandler(AbstractHandler):

    def get(self):
        logging.info("GOT CALLED")
        completed_sports_events = db.GqlQuery("SELECT * From SportsEvent WHERE completed = true")
        for current_offset in range(0, 10000, 100):
            logging.info("Starting with offset : %d" % current_offset)
            results = completed_sports_events.fetch(100, offset = current_offset)

            logging.info("Received : %d" % len(results))
            if len(results) > 0:
                for event in results:
                    event.completed = False
                    event.put()
            else:
                return

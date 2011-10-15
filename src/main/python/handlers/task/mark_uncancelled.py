import logging

from google.appengine.ext import db

from handlers.task.task import AbstractTaskHandler
from models.sports_event import SportsEvent

class MarkUncancelledTaskHandler(AbstractTaskHandler):
    def __init__(self):
        AbstractTaskHandler.__init__(self)

    def run_task(self):
        for offset in range(0, 5000, 25):
            logging.info("Fetching from %d" % offset)
            query = db.GqlQuery("SELECT * FROM SportsEvent ORDER BY start_date ASC")
            games = query.fetch(25, offset)
            logging.info("Got %d games" % len(games))
            for game in games:
                logging.info("GAME %s @ %s : %s, cancelled: %s" % (game.away_team.title, game.home_team.title, game.start_date_str, game.cancelled)) 
                logging.info("Marking this game as uncancelled")
                game.cancelled = False
                game.put()
             

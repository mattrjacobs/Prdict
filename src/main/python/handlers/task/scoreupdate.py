import datetime
import logging
import simplejson as json
import time

from google.appengine.ext import db

from handlers.task.task import AbstractTaskHandler
from models.sports_event import SportsEvent
from services.event_svc import EventService
from services.score_svc import ScoreService

class ScoreUpdateTaskHandler(AbstractTaskHandler):
    def __init__(self):
        AbstractTaskHandler.__init__(self)
        self.score_svc = ScoreService()
        self.event_svc = EventService()

    def run_task(self):
        utcnow = datetime.datetime.utcnow()
                
        uncancelled_query = db.GqlQuery("SELECT * FROM SportsEvent WHERE start_date < :1 AND completed = false AND cancelled = false ORDER BY start_date ASC", utcnow)
        current_games = uncancelled_query.fetch(25, 0)
                
        logging.info("NUM GAMES w/o score : %s" % len(current_games))
        for game in current_games:
            logging.info("THIS GAME %s @ %s : %s" % (game.away_team.title, game.home_team.title, game.start_date_str))
            if self.score_svc.can_get_score(game):
                #this prevents us from exceeding Fanfeedr QPS limit
                time.sleep(1)
                score = self.score_svc.get_score(game)
                logging.info("Received score : %s" % str(score))
                score["type"] = "sportsevent"
                score["ref_id"] = game.ref_id
                date_diff = utcnow - game.start_date
                if "home_team_score" in score and score["home_team_score"] == 0 and \
                   "away_team_score" in score and score["away_team_score"] == 0 and \
                   date_diff.days > 1:
                    logging.info("Marking this game as cancelled")
                    score["cancelled"] = "true"
                self.request.body = json.dumps(score)
                (_, _, _, _, _, msg, updated_entry) = self.event_svc.update_entry(game, self.request, "json")
                if msg:
                    logging.error("ERROR DURING SCORE UPDATE : %s" % msg)

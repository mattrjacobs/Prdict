from handlers.handler import AbstractHandler

import datetime
import logging
import simplejson as json
import time

from google.appengine.ext import db

from models.sports_event import SportsEvent
from services.event_svc import EventService
from services.score_svc import ScoreService

class ScoreUpdateTaskHandler(AbstractHandler):
    def __init__(self):
        self.CRON_HEADER = "X-AppEngine-Cron"
        self.score_svc = ScoreService()
        self.event_svc = EventService()

    # used for cron
    def get(self):
        if self.is_dev_host() or self.is_cron_request():
            self.handle_score_update()

    # used for task queue
    def post(self):
        logging.error("Shouldn't be receiving a POST here")

    def handle_score_update(self):
        query = db.GqlQuery("SELECT * FROM SportsEvent WHERE start_date < :1 AND completed = false ORDER BY start_date ASC", datetime.datetime.utcnow())
        current_games = query.fetch(25, 0)
        for game in current_games:
            if self.score_svc.can_get_score(game):
                #this prevents us from exceeding Fanfeedr QPS limit
                time.sleep(1)
                score = self.score_svc.get_score(game)
                score["type"] = "sportsevent"
                score["ref_id"] = game.ref_id
                self.request.body = json.dumps(score)
                (_, _, _, _, _, msg, updated_entry) = self.event_svc.update_entry(game, self.request, "json")
                if msg:
                    logging.error("ERROR DURING SCORE UPDATE : %s" % msg)
        
    def is_cron_request(self):
        hdr = self.get_header(self.CRON_HEADER)
        if hdr:
            return hdr.lower() == "true"
        else:
            return False

        

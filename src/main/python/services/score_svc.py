import datetime
import logging
import simplejson as json

from google.appengine.api import urlfetch

class ScoreService:
    API_KEY = "hqxv2tyfmmhu68zfn9nfsfsv"
    MAX_REQS_PER_HOUR = 25

    def __init__(self):
        self.current_hour = datetime.datetime.utcnow().hour
        self.reqs_this_hour = 0

    def can_get_score(self, event):
        hour_at_req = datetime.datetime.utcnow().hour
        logging.info("HOUR CHECKED : %s" % hour_at_req)
        logging.info("HOUR AT START : %s" % self.current_hour)
        if hour_at_req == self.current_hour:
            logging.info("MAX ALLOWED : %d" % ScoreService.MAX_REQS_PER_HOUR)
            logging.info("NUM USED : %d" % self.reqs_this_hour)
            if self.reqs_this_hour < ScoreService.MAX_REQS_PER_HOUR:
                logging.info("Allowing this request, since not at limit yet")
                self.reqs_this_hour = self.reqs_this_hour + 1
                return True
            else:
                logging.info("Already at limit for hour")
                return False
        else:
            logging.info("Allowing this request, since we're in new hour")
            self.current_hour = hour_at_req
            self.reqs_this_hour = 1
            return True

    def get_score(self, event):
        logging.info("Getting live score for : %s" % event.title)
        url = "http://ffapi.fanfeedr.com/basic/api/leagues/%s/events/%s?api_key=%s" % \
              (event.league.ref_id, event.ref_id, ScoreService.API_KEY)
        resp = urlfetch.fetch(url, deadline = 10)
        if resp.status_code == 200:
            json_resp = json.loads(resp.content)
            logging.info("STATUS : %s" % json_resp["status"])
            logging.info("LOWER : %s" % json_resp["status"].lower())
            logging.info("COMPLETED : %s" % str(json_resp["status"].lower() == "final"))
            return { 'home_team_score' : json_resp["home_team"]["score"],
                     'away_team_score' : json_resp["away_team"]["score"],
                     'completed' : str(json_resp["status"].lower() == "final") }
        else:
            logging.info("BAD STATUS : %d" % resp.status_code)
            logging.info("BAD RESP : %s" % resp.content)
            return { }

import datetime
import logging
import simplejson as json

from google.appengine.api import memcache
from google.appengine.api import urlfetch

class ScoreService:
    API_KEY = "hqxv2tyfmmhu68zfn9nfsfsv"
    MAX_REQS_PER_HOUR = 25
    CURRENT_HOUR_KEY = "score_current_hour"
    REQS_THIS_HOUR_KEY = "scores_this_hour"

    def can_get_score(self, event):
        current_hour = memcache.get(ScoreService.CURRENT_HOUR_KEY)
        if not current_hour:
            current_hour = datetime.datetime.utcnow().hour
            memcache.set(ScoreService.CURRENT_HOUR_KEY, current_hour)
        reqs_this_hour = memcache.get(ScoreService.REQS_THIS_HOUR_KEY)
        if not reqs_this_hour:
            reqs_this_hour = 0
        hour_at_req = datetime.datetime.utcnow().hour
        if hour_at_req == current_hour:
            if reqs_this_hour < ScoreService.MAX_REQS_PER_HOUR:
                memcache.set(ScoreService.REQS_THIS_HOUR_KEY, reqs_this_hour + 1)
                return True
            else:
                return False
        else:
            memcache.set(ScoreService.CURRENT_HOUR_KEY, hour_at_req)
            memcache.set(ScoreService.REQS_THIS_HOUR_KEY, 1)
            return True

    def get_score(self, event):
        logging.debug("Getting live score for : %s" % event.title)
        url = "http://ffapi.fanfeedr.com/basic/api/leagues/%s/events/%s?api_key=%s" % \
              (event.league.ref_id, event.ref_id, ScoreService.API_KEY)
        resp = urlfetch.fetch(url, deadline = 10)
        if resp.status_code == 200:
            json_resp = json.loads(resp.content)
            logging.info("ENTIRE GAME JSON : %s" % json_resp)
            logging.info("GAME STATUS : %s" % json_resp["status"])
            return { 'home_team_score' : json_resp["home_team"]["score"],
                     'away_team_score' : json_resp["away_team"]["score"],
                     'completed' : str(self.get_completed(json_resp)) }
        else:
            return { }

    def get_completed(self, json):
        if "status" not in json:
            return False
        else:
            status_str = json["status"]
            if status_str is None:
                return False
            else:
                return status_str.lower().strip() == "final"

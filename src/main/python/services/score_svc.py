import logging
import simplejson as json

from google.appengine.api import urlfetch

class ScoreService:
    API_KEY = "hqxv2tyfmmhu68zfn9nfsfsv"

    def __init__(self):
        pass

    def can_get_score(self, event):
        return True

    def get_score(self, event):
        logging.info("Getting live score for : %s" % event.title)
        url = "http://ffapi.fanfeedr.com/basic/api/leagues/%s/events/%s?api_key=%s" % \
              (event.league.ref_id, event.ref_id, ScoreService.API_KEY)
        resp = urlfetch.fetch(url, deadline = 10)
        if resp.status_code == 200:
            json_resp = json.loads(resp.content)
            return { 'home_team_score' : json_resp["home_team"]["score"],
                     'away_team_score' : json_resp["away_team"]["score"],
                     'completed' : str(json_resp["status"].lower() == "final") }
        else:
            return { }

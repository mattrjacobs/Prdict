from handlers.handler import AbstractHandler

import logging

from google.appengine.api import users
from google.appengine.ext import db

from models import event
from models import league
from models import prdict_user
from models import sport
from models.sports_event import SportsEvent
from models.team import Team

class TempTeamsAddHandler(AbstractHandler):
    def get(self):
        logging.info("Starting the teams add process...")
        query = SportsEvent.all()
        step_size = 20
        current_index = 0
        keep_going = True
        while keep_going:
            logging.info("Fetching range %d-%d" % (current_index, current_index + step_size))
            found = query.fetch(step_size, current_index)
            logging.info("Got %d" % len(found))
            for event in found:
                if len(event.teams) == 0:
                    #logging.info("Updating game : %s" % event.title)
                    #logging.info("HOME Team : %s" % event.home_team.title)
                    #logging.info("AWAY Team : %s" % event.away_team.title)
                    teams = [event.home_team.key(), event.away_team.key()]
                    event.teams = teams
                    event.put()
                    #logging.info("SAVED, new teams : %s" % event.teams)
            if (len(found)) == 0:
                keep_going = False
            else:
                current_index = current_index + step_size

        logging.info("Now at the end, to test, check all games w Colts")
        colts_key = db.Key(encoded="ag1kZXZ-cHJkaWN0YXBpciELEgVTcG9ydBgDDAsSBkxlYWd1ZRgIDAsSBFRlYW0YZAw")
        colts_query = db.Query(SportsEvent).filter("teams =", colts_key)
        colts_events = colts_query.fetch(30, 0)
        logging.info("FOUND %d Colts Events" % len(colts_events))
        for colts_event in colts_events:
            logging.info("TITLE : %s" % colts_event.title)

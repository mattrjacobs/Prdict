from handlers.handler import AbstractHandler

import logging

from google.appengine.api import users
from google.appengine.ext import db

from models import event
from models import league
from models import prdict_user
from models import sport
from models.team import Team

class TempTeamLogoAdder(AbstractHandler):
    def get(self):
        logging.info("Starting the logo add process...")
        query = Team.all()
        teams = query.fetch(300, 0)
        logging.info("Got %d teams" % len(teams))
        for team in teams:
            #logging.info("TITLE : %s" % team.title)
            #logging.info("LOCATION : %s" % team.location)
            #logging.info("LEAGUE : %s" % team.league.title)
            args = (team.league.title.lower(),
                    team.location.lower().replace(' ', '').replace('.', ''),
                    team.title.lower().replace(' ', ''))
            logo_url = "/img/logos/%s/%s_%s.png" % args
            #logging.info("PROPOSED_LOGO_URL : %s" % logo_url)
            #logging.info("CURRENT  LOGO URL : %s" % team.logo_url)
            if logo_url != team.logo_url:
                logging.info("PROPOSED_LOGO_URL : %s" % logo_url)
                logging.info("CURRENT  LOGO URL : %s" % team.logo_url)

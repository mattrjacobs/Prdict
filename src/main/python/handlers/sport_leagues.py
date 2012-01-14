import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from services.league_svc import LeagueService

class SportLeaguesHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.html = "sport_leagues.html"
        self.entry_html = "league.html"

    def get_max_results_allowed(self):
        return 100

    def get_default_max_results(self):
        return 10

    def get_parent_name(self):
        return "sport"

    def get_svc(self):
        return LeagueService()

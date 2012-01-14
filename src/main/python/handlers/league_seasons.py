import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from models.season import Season
from services.season_svc import SeasonService

class LeagueSeasonsHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.html = "league_seasons.html"
        self.entry_html = "season.html"

    def get_parent_name(self):
        return "league"

    def get_max_results_allowed(self):
        return 100

    def get_default_max_results(self):
        return 10

    def get_svc(self):
        return SeasonService()

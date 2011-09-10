import logging

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from models.league import League

class LeagueUiHandler(AbstractHandler, BaseAuthorizationHandler):
    @http_basic_auth
    def get(self, user, league_name):
        league = League.find_by_name(league_name)
        if league:
            self.render_html(league, league.get_teams(), user = user)
        else:
            self.set_404("html", user)

    def render_html(self, league, teams, msg = None, user = None):
        self.render_template("ui_league.html",
                             { 'current_user' : user,
                               'league' : league,
                               'teams' : teams,
                               'self_link' : self.request.url,
                               'msg' : msg })
        

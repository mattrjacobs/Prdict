import logging
import urllib

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from models.league import League
from models.team import Team

class TeamUiHandler(AbstractHandler, BaseAuthorizationHandler):
    @http_basic_auth
    def get(self, user, league_name, team_name):
        escaped_league_name = urllib.unquote(league_name)
        escaped_team_name = urllib.unquote(team_name)
        league = League.find_by_name(escaped_league_name)
        seasons = league.seasons
        team = Team.find_by_name(name = escaped_team_name, location = None, league = league)
        if team:
            self.render_html(team, seasons, user = user)
        else:
            self.set_404("html", user)

    def render_html(self, team, seasons, msg = None, user = None):
        self.render_template("ui_team.html",
                             { 'current_user' : user,
                               'team' : team,
                               'seasons' : seasons,
                               'self_link' : self.request.url,
                               'msg' : msg })
        

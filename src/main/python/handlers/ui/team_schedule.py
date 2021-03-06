import logging
import urllib

from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from models.league import League
from models.season import Season
from models.team import Team

class TeamScheduleUiHandler(AbstractHandler, BaseAuthorizationHandler):
    @http_basic_auth
    def get(self, user, league_name, team_name, season_name):
        escaped_league_name = urllib.unquote(league_name)
        escaped_team_name = urllib.unquote(team_name)
        escaped_season_name = urllib.unquote(season_name)
        league = League.find_by_name(escaped_league_name)
        team = Team.find_by_name(name = escaped_team_name, location = None, league = league)
        season = Season.find_by_league_and_name(league = league, name = escaped_season_name)
        if team and season:
            self.render_html(team = team, season = season, msg = None, user = user)
        else:
            self.set_404("html", user)


    def render_html(self, team, season, msg = None, user = None):
        self.render_template("ui_team_schedule.html",
                             { 'current_user' : user,
                               'team' : team,
                               'season' : season,
                               'self_link' : self.request.url,
                               'msg' : msg })

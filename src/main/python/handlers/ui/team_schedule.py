import logging

from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from models.league import League
from models.team import Team

class TeamScheduleUiHandler(AbstractHandler, BaseAuthorizationHandler):
    @http_basic_auth
    def get(self, user, league_name, team_name):
        league = League.find_by_name(league_name)
        team = Team.find_by_name(name = team_name, location = None, league = league)
        if team:
            self.render_html(team = team, msg = None, user = user)
        else:
            self.set_404("html", user)


    def render_html(self, team, msg = None, user = None):
        self.render_template("ui_team_schedule.html",
                             { 'current_user' : user,
                               'team' : team,
                               'self_link' : self.request.url,
                               'msg' : msg })

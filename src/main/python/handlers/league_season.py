"""Handles a request for a league"""
import httplib
import logging
import simplejson as json

from handlers.auth import BaseAuthorizationHandler
from handlers.member import MemberHandler
from models.league import League
from models.season import Season
from services.season_svc import SeasonService

class LeagueSeasonMemberHandler(MemberHandler, BaseAuthorizationHandler):
    """Handles a request for an season resource that is part of a league.
    MemberHandler has logic for HTTP operations
    LeagueAuthorizationHandler has logic for authorization."""
    def __init__(self):
        self.season_svc = SeasonService()
        self.html = "season.html"

    def render_html(self, entry, msg=None):
        """Renders an HTML Season"""
        current_user = self.get_prdict_user()
        self.render_template("season.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : False,
                               'entry' : entry,
                               'leagues' : self.get_all_leagues() })

    def render_atom(self, league):
        self.render_template('xml/season_atom.xml',
                             { 'entry' : entry, 'base_url' : self.baseurl() })

    def is_parent_of(self, league, season):
        return str(season.league.key()) == str(league.key())

    def get_svc(self):
        return self.season_svc

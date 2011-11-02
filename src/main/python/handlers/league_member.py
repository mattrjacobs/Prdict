"""Handles a request for a league"""
import httplib
import logging
import simplejson as json

from handlers.auth import BaseAuthorizationHandler
from handlers.member import MemberHandler
from models.league import League
from models.sport import Sport
from services.league_svc import LeagueService

class LeagueMemberHandler(MemberHandler, BaseAuthorizationHandler):
    """Handles a request for an league resource that is part of a sport.
    MemberHandler has logic for HTTP operations
    LeagueAuthorizationHandler has logic for authorization."""
    def __init__(self):
        self.league_svc = LeagueService()
        self.html = "league.html"

    def render_html(self, entry, msg=None):
        """Renders an HTML Event"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("league.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'entry' : entry,
                               'sports' : self.get_all_sports() })

    def is_parent_of(self, sport, league):
        return str(league.key()) in [str(l.key()) for l in sport.leagues]

    def get_svc(self):
        return self.league_svc

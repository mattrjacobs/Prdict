"""Handles a request for a league"""
import httplib
import logging
import simplejson as json

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.league import League
from models.sport import Sport
from services.league_svc import LeagueService

class LeagueHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an league resource.
    EntryHandler has logic for HTTP operations
    LeagueAuthorizationHandler has logic for authorization."""
    def __init__(self):
        self.league_svc = LeagueService()

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

    def render_atom(self, league):
        self.render_template('xml/league_atom.xml',
                             { 'entry' : entry, 'base_url' : self.baseurl() })

    def get_svc(self):
        return self.league_svc

    def get_html(self, entry):
        return "league.html"

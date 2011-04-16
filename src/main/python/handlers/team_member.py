"""Handles a request for a team"""
import httplib
import logging

from handlers.auth import BaseAuthorizationHandler
from handlers.member import MemberHandler
from models.league import League
from models.team import Team
from services.team_svc import TeamService

class TeamMemberHandler(MemberHandler, BaseAuthorizationHandler):
    """Handles a request for an team resource that is part of a league.
    EntryHandler has logic for HTTP operations
    LeagueAuthorizationHandler has logic for authorization."""
    def __init__(self):
        self.team_svc = TeamService()
        self.html = "team.html"

    def render_html(self, entry, msg=None):
        """Renders an HTML Team"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("team.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'entry' : entry,
                               'leagues' : self.get_all_leagues() })

    def render_atom(self, team):
        self.render_template('xml/team_atom.xml',
                             { 'entry' : entry, 'base_url' : self.baseurl() })

    def is_parent_of(self, league, team):
        return str(team.key()) in [str(t.key()) for t in league.teams]

    def get_svc(self):
        return self.team_svc

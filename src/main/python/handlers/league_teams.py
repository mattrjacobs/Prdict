import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from services.team_svc import TeamService

class LeagueTeamsHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.team_svc = TeamService()
        self.html = "league_teams.html"
        self.entry_html = "team.html"

    def get_entries(self, parent, limit = 100, offset = 0):
        if parent:
            query = db.GqlQuery("SELECT * FROM Team where league = :1 ORDER BY title", parent.key())
            return query.fetch(limit, offset)
        else:
            return []

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        self.render_template("league_teams.html",
                             { 'current_user' : self.get_prdict_user(),
                               'parent' : parent,
                               'entries' : entries,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'msg' : msg })
        
    def render_atom(self, parent, entries, prev_link=None, next_link=None,
                    msg = None):
        raise "Not implemented yet"

    def get_parent_name(self):
        return "league"

    def get_entries_name(self):
        return "teams"

    def get_svc(self):
        return self.team_svc
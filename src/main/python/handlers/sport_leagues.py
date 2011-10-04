import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from services.league_svc import LeagueService

class SportLeaguesHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.league_svc = LeagueService()
        self.html = "sport_leagues.html"
        self.entry_html = "league.html"

    def get_entries(self, parent, query, limit = 25, offset = 0):
        if parent:
            if query:
                gql_query = db.GqlQuery("SELECT * FROM League where sport = :1 AND %s = :2 ORDER BY title" % query[0], parent.key(), query[1])
            else:
                gql_query = db.GqlQuery("SELECT * FROM League where sport = :1 ORDER BY title", parent.key())                
            return gql_query.fetch(limit, offset)
        else:
            return []

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg=None, user = None):
        self.render_template("sport_leagues.html",
                             { 'current_user' : user,
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
        return "sport"

    def get_entries_name(self):
        return "leagues"

    def get_svc(self):
        return self.league_svc

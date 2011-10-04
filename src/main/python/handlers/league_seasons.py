import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from models.season import Season
from services.season_svc import SeasonService

class LeagueSeasonsHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.season_svc = SeasonService()
        self.html = "league_seasons.html"
        self.entry_html = "season.html"

    def get_entries(self, parent, query, limit = 100, offset = 0):
        if parent:
            if query:
                gql_query = db.GqlQuery("SELECT * FROM Season where league = :1 AND %s = :2 ORDER BY title" % query[0], parent.key(), query[1])
            else:
                gql_query = db.GqlQuery("SELECT * FROM Season where league = :1 ORDER BY title", parent.key())
            return gql_query.fetch(limit, offset)
        else:
            return []

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg=None, user = None):
        self.render_template(self.html,
                             { 'current_user' : user,
                               'parent' : parent,
                               'entries' : entries,
                               'leagues' : self.get_all_leagues(),
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
        return "seasons"

    def get_svc(self):
        return self.season_svc

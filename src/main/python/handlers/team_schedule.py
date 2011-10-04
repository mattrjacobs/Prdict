import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from services.team_svc import TeamService

class TeamScheduleHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.team_svc = TeamService()
        self.html = "team_schedule.html"

    def get_entries(self, parent, query, limit, offset = 0):
        # ignoring the query here for now
        if parent:
            home_query = db.GqlQuery("SELECT * FROM SportsEvent where home_team = :1 ORDER BY start_date ASC", parent.key())
            away_query = db.GqlQuery("SELECT * FROM SportsEvent where away_team = :1 ORDER BY start_date ASC", parent.key())
            all_home_games = home_query.fetch(1000, 0)
            all_away_games = away_query.fetch(1000, 0)
            all_sorted_games = self.merge_lists(all_home_games, all_away_games)
            return all_sorted_games[offset:offset + limit]
        else:
            return []

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg=None, user = None):
        self.render_template(self.html,
                             { 'current_user' : user,
                               'parent' : parent,
                               'entries' : entries,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'msg' : msg })
        
    def get_parent_name(self):
        return "team"

    def get_entries_name(self):
        return "schedule"

    def get_svc(self):
        return self.team_svc

    def merge_lists(self, home_list, away_list):
        home_list.extend(away_list)
        return sorted(home_list, key = lambda game: game.start_date)

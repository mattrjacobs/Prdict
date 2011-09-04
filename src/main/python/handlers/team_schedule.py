import logging

from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler
from services.team_svc import TeamService

class TeamScheduleHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.team_svc = TeamService()
        self.html = "team_schedule.html"

    def get_entries(self, parent, limit = 100, offset = 0):
        if offset > 0:
            raise "Not supporting offset in this query"
        if parent:
            home_query = db.GqlQuery("SELECT * FROM SportsEvent where home_team = :1 ORDER BY start_date ASC", parent.key())
            away_query = db.GqlQuery("SELECT * FROM SportsEvent where away_team = :1 ORDER BY start_date ASC", parent.key())
            home_games = home_query.fetch(limit/2, 0)
            away_games = away_query.fetch(limit/2, 0)
            all_games = []
            for i in range(0, len(home_games) + len(away_games)):
                if len(away_games) == 0:
                    all_games.append(home_games[0])
                    home_games.pop(0)
                elif len(home_games) == 0:
                    all_games.append(away_games[0])
                    away_games.pop(0)
                elif home_games[0].start_date < away_games[0].start_date:
                    all_games.append(home_games[0])
                    home_games.pop(0)
                else:
                    all_games.append(away_games[0])
                    away_games.pop(0)

            return all_games
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
        
    def render_atom(self, parent, entries, prev_link=None, next_link=None,
                    msg = None):
        raise "Not implemented yet"

    def get_parent_name(self):
        return "team"

    def get_entries_name(self):
        return "schedule"

    def get_svc(self):
        return self.team_svc

import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import BaseAuthorizationHandler, http_basic_auth
from handlers.handler import AbstractHandler
from services.team_svc import TeamService
from utils.constants import Constants

class TeamScheduleHandler(AbstractHandler, BaseAuthorizationHandler):
    def __init__(self):
        self.team_svc = TeamService()
        self.html = "team_schedule.html"

    @http_basic_auth
    def get(self, user, team_key, season_key):
        team = self.get_authorized_entry(team_key, "read")
        if not team:
            return
        season = self.get_authorized_entry(season_key, "read")
        if not season:
            return
        query = self.get_query()
        games = self.get_entries(team, query, limit = 1000)
        (content_type, vary) = self.get_read_content_type()
        if vary:
            self.set_header("Vary","Accept")
        if content_type == "atom":
            self.set_header("Content-Type", Constants.XML_ENCODING)
            self.render_atom(team, season, games)
            return
        elif content_type == "json":
            self.set_header("Content-Type", Constants.JSON_ENCODING)
            self.render_json(team, season, games)
            return
        elif content_type == "html":
            self.render_html(team, season, games, None, user)
            return
        else:
            logging.error("Received a content type I can't handle %s" % content_type)
            
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

    def render_html(self, team, season, games, prev_link=None, next_link=None,
                    msg=None, user = None):
        self.render_template(self.html,
                             { 'current_user' : user,
                               'parent' : team,
                               'season' : season,
                               'entries' : games,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'msg' : msg })

    def render_json(self, team, season, games):
        team_json = team.to_json()
        season_json = season.to_json()
        games_json = [json.loads(game.to_json()) for game in games]
        self.render_string(json.dumps({ 'team' : json.loads(team_json),
                                        'season' : json.loads(season_json),
                                        'games' : games_json}))
        
    def get_parent_name(self):
        return "team"

    def get_entries_name(self):
        return "schedule"

    def get_svc(self):
        return self.team_svc

    def merge_lists(self, home_list, away_list):
        home_list.extend(away_list)
        return sorted(home_list, key = lambda game: game.start_date)

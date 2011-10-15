from google.appengine.ext import db

import logging
import simplejson as json

from abstract_model import AbstractModel
from event import Event
from league import League
from season import Season
from team import Team

class SportsEventEncoder(json.JSONEncoder):
    def default(self, event):
        if not isinstance(event, SportsEvent):
            return

        return { 'title' : event.title,
                 'description' : event.description,
                 'home_team' : { 'uri' : event.home_team.relative_url,
                                 'location' : event.home_team.location,
                                 'title' : event.home_team.title,
                                 'score' : event.home_team_score },
                 'away_team' : { 'uri' : event.away_team.relative_url,
                                 'location' : event.away_team.location,
                                 'title' : event.away_team.title,
                                 'score' : event.away_team_score },
                 'league' : { 'uri' : event.league.relative_url,
                              'title' : event.league.title },
                 'season' : { 'uri' : event.season.relative_url,
                              'title' : event.season.title },
                 'completed' : event.completed,
                 'cancelled' : event.cancelled,
                 'game_kind' : event.game_kind,
                 'ref_id' : event.ref_id,
                 'self' : event.relative_url,
                 'key' : str(event.key()),
                 'start_date' : event.start_date_str,
                 'nice_start_date_est' : event.nice_start_date_est,
                 'end_date' : event.end_date_str,
                 'created' : event.isoformat_created,
                 'updated' : event.isoformat_updated }

class SportsEvent(Event):
    league = db.ReferenceProperty(required=True, reference_class=League)
    season = db.ReferenceProperty(required=True, reference_class=Season)
    home_team = db.ReferenceProperty(required=True,
                                     collection_name='home_team',
                                     reference_class=Team)
    away_team = db.ReferenceProperty(required=True,
                                     collection_name='away_team',
                                     reference_class=Team)
    completed = db.BooleanProperty(required=True, default=False)
    cancelled = db.BooleanProperty(required=True, default=False)
    home_team_score = db.IntegerProperty(required=False)
    away_team_score = db.IntegerProperty(required=False)
    ref_id = db.StringProperty(required=False)
    game_kind = db.CategoryProperty(required=True,
                                    default="Regular Season",
                                    choices=("Regular Season",
                                             "Preseason",
                                             "Postseason"))
    
    @staticmethod
    def validate_params(params):
        (is_base_event_valid, base_event_error_msg) = \
                              Event.validate_params(params)

        error_msgs = []
        league = home_team_str = away_team_str = completed_str = cancelled_str = \
                 home_team_score_str = \
                 away_team_score_str = ref_id = game_kind = season_uri = season = None
        sports_event_ok = True

        if "league" in params:
            league = params["league"]
        if "season_uri" in params:
            season_uri = params["season_uri"]
        if "home_team_str" in params:
            home_team_str = params["home_team_str"]
        if "away_team_str" in params:
            away_team_str = params["away_team_str"]
        if "completed_str" in params:
            completed_str = params["completed_str"]
        if "cancelled_str" in params:
            cancelled_str = params["cancelled_str"]
        if "home_team_score_str" in params:
            home_team_score_str = params["home_team_score_str"]
        if "away_team_score_str" in params:
            away_team_score_str = params["away_team_score_str"]
        if "ref_id" in params:
            ref_id = params["ref_id"]
        if "game_kind" in params:
            game_kind = params["game_kind"]

        if not league:
            error_msgs.append("Sports Event must have a league")
            sports_event_ok = False
        if not season_uri:
            error_msgs.append("Sports Event must have a season")
            sports_event_ok = False
        if season_uri:
            season = Season.parse_season_uri(season_uri)
            if not season:
                error_msgs.append("Could not parse season URI : %s" % season_uri)
                sports_event_ok = False
            else:
                params["season"] = season
        if not home_team_str:
            error_msgs.append("Sports Event must have a home team")
            sports_event_ok = False
        if not away_team_str:
            error_msgs.append("Sports event must have an away team")
            sports_event_ok = False
        if home_team_str:
            home_team = Team.parse_team_uri(home_team_str)
            if not home_team:
                error_msgs.append("Could not parse home team : %s" % home_team_str)
                sports_event_ok = False
            else:
                params["home_team"] = home_team
        if away_team_str:
            away_team = Team.parse_team_uri(away_team_str)
            if not away_team:
                error_msgs.append("Could not parse away team : %s" % away_team_str)
                sports_event_ok = False
            else:
                params["away_team"] = away_team
        if league and home_team and not str(league.key()) == str(home_team.league.key()):
            error_msgs.append("Home team and league are incompatible")
            sports_event_ok = False
        if league and away_team and not str(league.key()) == str(away_team.league.key()):
            error_msgs.append("Away team and league are incompatible")
            sports_event_ok = False
        if home_team and away_team and str(home_team.key()) == str(away_team.key()):
            error_msgs.append("Team cannot play itself")
            sports_event_ok = False
        if league and season and not str(league.key()) == str(season.league.key()):
            error_msgs.append("Season must be part of league")
            sports_event_ok = False
        if completed_str:
            if not completed_str.lower() in ("true", "false"):
                error_msgs.append("Could not parse completed for Sports Event")
                sports_event_ok = False
            else:
                params["completed"] = completed_str.lower() == "true"
        if cancelled_str:
            if not cancelled_str.lower() in ("true", "false"):
                error_msgs.append("Could not parse cancelled for Sports Event")
                sports_event_ok = False
            else:
                params["cancelled"] = cancelled_str.lower() == "true"
        if home_team_score_str:
            if not AbstractModel.parse_int(home_team_score_str):
                error_msgs.append("Could not parse home team score for Sports Event")
                sports_event_ok = False
            else:
                params["home_team_score"] = int(home_team_score_str)
        else:
            params["home_team_score"] = 0

        if away_team_score_str:
            if not AbstractModel.parse_int(away_team_score_str):
                error_msgs.append("Could not parse away team score for Sports Event")
                sports_event_ok = False
            else:
                params["away_team_score"] = int(away_team_score_str)
        else:
            params["away_team_score"] = 0
        if game_kind:
            if not game_kind.lower() in ('regular season', 'preseason', 'postseason'):
                error_msgs.append("Invalid game kind for Sports Event")
                sports_event_ok = False
        else:
            params["game_kind"] = "Regular Season"

        if not sports_event_ok:
            return (False, ",".join(error_msgs))
        else:
            return (True, None)

    def validate_subset_params(self, params):
        (is_base_event_valid, base_event_error_msg) = \
                              super(SportsEvent, self).validate_subset_params(params)

        error_msgs = []
        if base_event_error_msg:
            error_msgs.append(base_event_error_msg)
        league = home_team_str = away_team_str = completed_str = cancelled_str = \
                 home_team_score_str = \
                 away_team_score_str = game_kind = home_team = away_team = season_uri = None
        sports_event_ok = is_base_event_valid

        if "league" in params:
            league = params["league"]
        if "season_uri" in params:
            season_uri = params["season_uri"]
        if "home_team_str" in params:
            home_team_str = params["home_team_str"]
        if "away_team_str" in params:
            away_team_str = params["away_team_str"]
        if "completed_str" in params:
            completed_str = params["completed_str"]
        if "cancelled_str" in params:
            cancelled_str = params["cancelled_str"]
        if "home_team_score_str" in params:
            home_team_score_str = params["home_team_score_str"]
        if "away_team_score_str" in params:
            away_team_score_str = params["away_team_score_str"]
        if "ref_id" in params:
            ref_id = params["ref_id"]
        if "game_kind" in params:
            game_kind = params["game_kind"]

        if home_team_str:
            home_team = Team.parse_team_uri(home_team_str)
            if not home_team:
                error_msgs.append("Could not parse home team : %s" % home_team_str)
                sports_event_ok = False

        if away_team_str:
            away_team = Team.parse_team_uri(away_team_str)
            if not away_team:
                error_msgs.append("Could not parse away team : %s" % away_team_str)
                sports_event_ok = False

        if league:
            if home_team and not str(league.key()) == \
                   str(home_team.league.key()):
                error_msgs.append("Home team and league are incompatible")
                sports_event_ok = False
            if not home_team and not str(league.key()) == \
                   str(self.home_team.key()):
                error_msgs.append("Home team and league are incompatible")
                sports_event_ok = False
            if away_team and not str(league.key()) == \
                   str(away_team.league.key()):
                error_msgs.append("Away team and league are incompatible")
                sports_event_ok = False
            if not away_team and not str(league.key()) == \
                   str(self.away_team.key()):
                error_msgs.append("Away team and league are incompatible")
                sports_event_ok = False
        if season_uri:
            season = Season.parse_season_uri(season_uri)
            if not season:
                error_msgs.append("Could not parse season URI : %s" % season_uri)
                sports_event_ok = False
            elif league and not str(league.key()) == str(season.league.key()):
                error_msgs.append("Season and league are incompatible")
                sports_event_ok = False
            else:
                params["season"] = season
        if home_team:
            if away_team and str(home_team.key()) == str(away_team.key()):
                error_msgs.append("Team cannot play itself")
                sports_event_ok = False
            if not away_team and str(home_team.key()) == \
                   str(self.away_team.key()):
                error_msgs.append("Team cannot play itself")
                sports_event_ok = False
        if away_team:
            if not home_team and str(away_team.key()) == \
                   str(self.home_team.key()):
                error_msgs.append("Team cannot play itself")
                sports_event_ok = False
        if completed_str:
            if not completed_str.lower() in ("true", "false"):
                error_msgs.append("Could not parse completed for Sports Event")
                completed_ok = False
            else:
                params["completed"] = completed_str.lower() == "true"
        if cancelled_str:
            if not cancelled_str.lower() in ("true", "false"):
                error_msgs.append("Could not parse cancelled for Sports Event")
                cancelled_ok = False
            else:
                params["cancelled"] = cancelled_str.lower() == "true"
        if home_team_score_str:
            if not AbstractModel.parse_int(home_team_score_str):
                error_msgs.append("Could not parse home team score for Sports Event")
                sports_event_ok = False            
            else:
                params["home_team_score"] = int(home_team_score_str)
        else:
            params["home_team_score"] = 0

        if away_team_score_str:
            if not AbstractModel.parse_int(away_team_score_str):
                error_msgs.append("Could not parse away team score for Sports Event")
                sports_event_ok = False
            else:
                params["away_team_score"] = int(away_team_score_str)
        else:
            params["away_team_score"] = 0
        if game_kind:
            if not game_kind.lower() in ('regular season', 'preseason', 'postseason'):
                error_msgs.append("Invalid game kind for Sports Event")
                sports_event_ok = False
        else:
            params["game_kind"] = "Regular Season"

        if not sports_event_ok:
            return (False, ",".join(error_msgs))
        else:
            return (True, None)

    def to_json(self):
        return SportsEventEncoder(sort_keys = True).encode(self)

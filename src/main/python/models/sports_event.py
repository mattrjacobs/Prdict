from google.appengine.ext import db

import logging
import simplejson as json

from abstract_model import AbstractModel
from event import Event
from team import Team

class SportsEventEncoder(json.JSONEncoder):
    def default(self, event):
        if not isinstance(event, SportsEvent):
            return

        def convert_team_to_json(team):
            return { 'title' : team.title,
                     'location' : team.location,
                     'link' : team.relative_url }

        league_json = { 'title' : event.league.title,
                        'link' : event.league.relative_url }
        
        return { 'title' : event.title,
                 'description' : event.description,
                 'home_team' : convert_team_to_json(event.home_team),
                 'away_team' : convert_team_to_json(event.away_team),
                 'league' : league_json,
                 'completed' : event.completed,
                 'home_team_score' : event.home_team_score,
                 'away_team_score' : event.away_team_score,
                 'game_kind' : event.game_kind,
                 'link' : event.relative_url,
                 'start_date' : event.start_date_str,
                 'end_date' : event.end_date_str,
                 'created' : event.isoformat_created,
                 'updated' : event.isoformat_updated }

class SportsEvent(Event):
    league = db.ReferenceProperty(required=True)
    home_team = db.ReferenceProperty(required=True,
                                     collection_name='home_team',
                                     reference_class=Team)
    away_team = db.ReferenceProperty(required=True,
                                     collection_name='away_team',
                                     reference_class=Team)
    completed = db.BooleanProperty(required=True, default=False)
    home_team_score = db.IntegerProperty(required=False)
    away_team_score = db.IntegerProperty(required=False)
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
        league = home_team_str = away_team_str = completed = home_team_score = \
                 away_team_score = game_kind = None
        sports_event_ok = True

        if "league" in params:
            league = params["league"]
        if "home_team_str" in params:
            home_team_str = params["home_team_str"]
        if "away_team_str" in params:
            away_team_str = params["away_team_str"]
        if "completed" in params:
            completed = params["completed"]
        if "home_team_score" in params:
            home_team_score = params["home_team_score"]
        if "away_team_score" in params:
            away_team_score = params["away_team_score"]
        if "game_kind" in params:
            game_kind = params["game_kind"]

        if not league:
            error_msgs.append("Sports Event must have a league")
            sports_event_ok = False
        if not home_team_str:
            error_msgs.append("Sports Event must have a home team")
            sports_event_ok = False
        if not away_team_str:
            error_msgs.append("Sports event must have an away team")
            sports_event_ok = False
        if home_team_str:
            home_team = Team.parse_team_str(home_team_str)
            if not home_team:
                error_msgs.append("Could not parse home team : %s" % home_team_str)
                sports_event_ok = False
            else:
                params["home_team"] = home_team
        if away_team_str:
            away_team = Team.parse_team_str(away_team_str)
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
        if completed:
            if not completed.lower() in ("true", "false"):
                error_msgs.append("Could not parse completed for Sports Event")
                sports_event_ok = False
            else:
                params["completed"] = completed.lower() == "true"
        if home_team_score:
            if not AbstractModel.parse_int(home_team_score):
                error_msgs.append("Could not parse home team score for Sports Event")
                sports_event_ok = False            
            else:
                params["home_team_score"] = int(home_team_score)
        else:
            params["home_team_score"] = 0

        if away_team_score:
            if not AbstractModel.parse_int(away_team_score):
                error_msgs.append("Could not parse away team score for Sports Event")
                sports_event_ok = False
            else:
                params["away_team_score"] = int(away_team_score)
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
        league = home_team_str = away_team_str = completed = home_team_score = \
                 away_team_score = game_kind = home_team = away_team = None
        sports_event_ok = is_base_event_valid

        if "league" in params:
            league = params["league"]
        if "home_team_str" in params:
            home_team_str = params["home_team_str"]
        if "away_team_str" in params:
            away_team_str = params["away_team_str"]
        if "completed" in params:
            completed = params["completed"]
        if "home_team_score" in params:
            home_team_score = params["home_team_score"]
        if "away_team_score" in params:
            away_team_score = params["away_team_score"]
        if "game_kind" in params:
            game_kind = params["game_kind"]

        if home_team_str:
            home_team = Team.parse_team_str(home_team_str)
            if not home_team:
                error_msgs.append("Could not parse home team : %s" % home_team_str)
                sports_event_ok = False

        if away_team_str:
            away_team = Team.parse_team_str(away_team_str)
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
        if completed:
            if not completed.lower() in ("true", "false"):
                error_msgs.append("Could not parse completed for Sports Event")
                sports_event_ok = False
            else:
                params["completed"] = completed.lower() == "true"
        if home_team_score:
            if not AbstractModel.parse_int(home_team_score):
                error_msgs.append("Could not parse home team score for Sports Event")
                sports_event_ok = False            
            else:
                params["home_team_score"] = int(home_team_score)
        else:
            params["home_team_score"] = 0

        if away_team_score:
            if not AbstractModel.parse_int(away_team_score):
                error_msgs.append("Could not parse away team score for Sports Event")
                sports_event_ok = False
            else:
                params["away_team_score"] = int(away_team_score)
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

import logging
import simplejson as json

from google.appengine.ext import db

from models.event import Event
from models.sports_event import SportsEvent
from models.team import Team
from services.base_svc import BaseService

class EventService(BaseService):
    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        description = self.get_json_str(parsed_body, "description")
        start_date_str = self.get_json_str(parsed_body, "start_date")
        end_date_str = self.get_json_str(parsed_body, "end_date")
        type = self.get_json_str(parsed_body, "type")

        if type.lower() == "sportsevent":
            home_team_str = self.get_json_str(parsed_body, "home_team")
            away_team_str = self.get_json_str(parsed_body, "away_team")
            league = self.get_league_from_request(
                request, self.get_json_str(parsed_body, "league"))
            completed = self.get_json_str(parsed_body, "completed")
            home_team_score = self.get_json_str("home_team_score")
            away_team_score = self.get_json_str("away_team_score")
            game_kind = self.get_json_str("game_kind")
            return self.__create_sports_event_param_map(
                "sportsevent", title, description, start_date_str, end_date_str,
                home_team_str, away_team_str, league, completed, home_team_score,
                away_team_score, game_kind)
        else:
            return self.__create_event_param_map(
                "event", title, description, start_date_str, end_date_str)

    def get_form_params(self, request):
        title = request.get("title")
        description = request.get("description")
        start_date_str = request.get("start_date")
        end_date_str = request.get("end_date")
        type = request.get("type")

        if type.lower() == "sportsevent":
            home_team_str = request.get("home_team")
            away_team_str = request.get("away_team")
            league = self.get_league_from_request(request, request.get("league"))
            completed = request.get("completed")
            home_team_score = request.get("home_team_score")
            away_team_score = request.get("away_team_score")
            game_kind = request.get("game_kind")
            return self.__create_sports_event_param_map(
                "sportsevent", title, description, start_date_str, end_date_str,
                home_team_str, away_team_str, league, completed, home_team_score,
                away_team_score, game_kind)
        else:
            return self.__create_event_param_map(
                "event", title, description, start_date_str, end_date_str)

    def __create_event_param_map(self, type, title, description,
                                 start_date_str, end_date_str):
        params = { }
        if type is not None:
            params["type"] = type
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description
        if start_date_str is not None:
            params["start_date_str"] = start_date_str
        if end_date_str is not None:
            params["end_date_str"] = end_date_str

        return params

    def __create_sports_event_param_map(self, type, title, description,
                                        start_date_str, end_date_str, home_team_str,
                                        away_team_str, league,
                                        completed, home_team_score,
                                        away_team_score, game_kind):
        params = self.__create_event_param_map(type, title, description,
                                               start_date_str, end_date_str)
        if home_team_str is not None:
            params["home_team_str"] = home_team_str
        if away_team_str is not None:
            params["away_team_str"] = away_team_str
        if league is not None:
            params["league"] = league
        if completed is not None:
            params["completed"] = completed
        if home_team_score is not None:
            params["home_team_score"] = home_team_score
        if away_team_score is not None:
            params["away_team_score"] = away_team_score
        if game_kind is not None:
            params["game_kind"] = game_kind

        return params
    
    def validate_params(self, params):
        if not "type" in params:
            return (False, "Could not determine type of event")
        type = params["type"].lower()
        if type == "event":
            return Event.validate_params(params)
        elif type == "sportsevent":
            return SportsEvent.validate_params(params)
        else:
            return (False, "Could not determine type of event")

    def validate_subset_params(self, event, params):
        return event.validate_subset_params(params)

    def create_entry_from_params(self, params):
        type = params["type"]
        if type == "event":
            new_event = Event(title = params["title"],
                              description = params["description"],
                              start_date = params["start_date"],
                              end_date = params["end_date"])
            new_event.put()
            return new_event
        if type == "sportsevent":
            new_sports_event = \
                SportsEvent(title = params["title"],
                            description = params["description"],
                            start_date = params["start_date"],
                            end_date = params["end_date"],
                            league = params["league"],
                            home_team = params["home_team"],
                            away_team = params["away_team"],
                            completed = params["completed"],
                            home_team_score = params["home_team_score"],
                            away_team_score = params["away_team_score"],
                            game_kind = params["game_kind"])
            new_sports_event.put()
            return new_sports_event

    def update_entry_from_params(self, event, params):
        if "title" in params:
            event.title = params["title"]
        if "description" in params:
            event.description = params["description"]
        if "start_date" in params:
            event.start_date = params["start_date"]
        if "end_date" in params:
            event.end_date = params["end_date"]
        type = params["type"]
        if type == "sportsevent":
            if "completed" in params:
                event.completed = params["completed"]
            if "home_team_score" in params:
                event.home_team_score = params["home_team_score"]
            if "away_team_score" in params:
                event.away_team_score = params["away_team_score"]
            if "league" in params:
                event.league = params["league"]
            if "home_team" in params:
                event.home_team = params["home_team"]
            if "away_team" in params:
                event.away_team = params["away_team"]
            if "game_kind" in params:
                event.game_kind = params["game_kind"]

        event.put()
        return event
        
        

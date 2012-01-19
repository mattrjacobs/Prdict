from datetime import datetime
import logging
import simplejson as json

from google.appengine.ext import db

from models.event import Event
from models.season import Season
from models.sports_event import SportsEvent
from models.team import Team
from services.base_svc import BaseService
from services.league_svc import LeagueService

class EventService(BaseService):
    get_now = lambda foo: datetime.utcnow()
    RECENT_EVENTS_FILTERS = [["end_date <", get_now]]
    FUTURE_EVENTS_FILTERS = [["start_date >", get_now]]
    IN_PROGRESS_PLUS_FILTERS = [["start_date <", get_now]]
    
    def get_model(self):
        return SportsEvent

    def get_entry_list_name(self):
        return "events"

    def _translate_query_into_db_query(self, query):
        logging.info("QUERY : %s" % query)
        if query[0] == "league":
            lookup_league = LeagueService.get_league_by_name(query[1])
            if lookup_league:
                return ["league =", lookup_league.key()]
        return None

    def get_count_of_recent_events(self, query):
        return self.get_arbitrary_count(self.RECENT_EVENTS_FILTERS, query)

    def get_count_of_future_events(self, query):
        return self.get_arbitrary_count(self.FUTURE_EVENTS_FILTERS, query)
    
    def get_count_of_inprogress_events(self, query):
        # gets 100 events that have already started
        list_of_start_in_past = self.get_arbitrary_entry_list(self.IN_PROGRESS_PLUS_FILTERS,
                                                              query, "-start_date", [0, 100])
        utcnow = datetime.utcnow()
        inprogress = 0
        for start_in_past in list_of_start_in_past:
            if start_in_past.end_date > utcnow:
                inprogress = inprogress + 1
        return inprogress

    def get_recent_events(self, pagination_params, query):
        return self.get_arbitrary_entry_list(self.RECENT_EVENTS_FILTERS, query,
                                             "-end_date", pagination_params)

    def get_future_events(self, pagination_params, query):
        return self.get_arbitrary_entry_list(self.FUTURE_EVENTS_FILTERS, query,
                                             "start_date", pagination_params)

    def get_inprogress_events(self, pagination_params, query):
        # gets 100 events that have already started
        list_of_start_in_past = self.get_arbitrary_entry_list(self.IN_PROGRESS_PLUS_FILTERS,
                                                              query, "-start_date", [0, 100])
        utcnow = datetime.utcnow()
        inprogress = []
        for start_in_past in list_of_start_in_past:
            if start_in_past.end_date > utcnow:
                inprogress.append(start_in_past)
        return inprogress[pagination_params[0]: pagination_params[0] + pagination_params[1]]

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

        if type:
            if type.lower() == "sportsevent":
                home_team_str = self.get_json_str(parsed_body, "home_team")
                away_team_str = self.get_json_str(parsed_body, "away_team")
                league = self.get_league_from_request(
                    request, self.get_json_str(parsed_body, "league"))
                season_uri = self.get_json_str(parsed_body, "season")
                completed = self.get_json_str(parsed_body, "completed")
                cancelled = self.get_json_str(parsed_body, "cancelled")
                home_team_score = self.get_json_str(parsed_body, "home_team_score")
                away_team_score = self.get_json_str(parsed_body, "away_team_score")
                ref_id = self.get_json_str(parsed_body, "ref_id")
                game_kind = self.get_json_str(parsed_body, "game_kind")
                return self.__create_sports_event_param_map(
                    "sportsevent", title, description, start_date_str, end_date_str,
                    home_team_str, away_team_str, league, season_uri, completed,
                    cancelled, home_team_score, away_team_score, ref_id, game_kind)
            elif type.lower() == "event":
                return self.__create_event_param_map(
                    "event", title, description, start_date_str, end_date_str)
            else:
                return {}
            
        else:
            return {}

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        description = self.get_form_str(request, "description")
        start_date_str = self.get_form_str(request, "start_date")
        end_date_str = self.get_form_str(request, "end_date")
        type = self.get_form_str(request, "type")

        if type:
            if type.lower() == "sportsevent":
                home_team_str = self.get_form_str(request, "home_team")
                away_team_str = self.get_form_str(request, "away_team")
                league = self.get_league_from_request(request, self.get_form_str(request, "league"))
                season_uri = self.get_form_str(request, "season")
                completed = self.get_form_str(request, "completed")
                cancelled = self.get_form_str(request, "cancelled")
                home_team_score = self.get_form_str(request, "home_team_score")
                away_team_score = self.get_form_str(request, "away_team_score")
                ref_id = self.get_form_str(request, "ref_id")
                game_kind = self.get_form_str(request, "game_kind")
                return self.__create_sports_event_param_map(
                    "sportsevent", title, description, start_date_str, end_date_str,
                    home_team_str, away_team_str, league, season_uri, completed,
                    cancelled, home_team_score, away_team_score, ref_id, game_kind)
            elif type.lower() == "event":
                return self.__create_event_param_map(
                    "event", title, description, start_date_str, end_date_str)
            else:
                return {}
        else:
            return {}
            
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
                                        away_team_str, league, season_uri,
                                        completed, cancelled, home_team_score,
                                        away_team_score, ref_id, game_kind):
        params = self.__create_event_param_map(type, title, description,
                                               start_date_str, end_date_str)
        if home_team_str is not None:
            params["home_team_str"] = home_team_str
        if away_team_str is not None:
            params["away_team_str"] = away_team_str
        if league is not None:
            params["league"] = league
        if season_uri is not None:
            params["season_uri"] = season_uri
        if completed is not None:
            params["completed_str"] = completed
        if cancelled is not None:
            params["cancelled_str"] = cancelled
        if home_team_score is not None:
            params["home_team_score_str"] = home_team_score
        if away_team_score is not None:
            params["away_team_score_str"] = away_team_score
        if ref_id is not None:
            params["ref_id"] = ref_id
        else:
            params["ref_id"] = ""
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
            if "description" in params:
                new_event = Event(title = params["title"],
                                  description = params["description"],
                                  start_date = params["start_date"],
                                  end_date = params["end_date"])
            else:
                new_event = Event(title = params["title"],
                                  start_date = params["start_date"],
                                  end_date = params["end_date"])
            new_event.put()
            return new_event
        if type == "sportsevent":
            if "description" in params:
                new_sports_event = SportsEvent(title = params["title"],
                                               description = params["description"],
                                               start_date = params["start_date"],
                                               end_date = params["end_date"],
                                               league = params["league"],
                                               season = params["season"],
                                               home_team = params["home_team"],
                                               away_team = params["away_team"],
                                               completed = params["completed"],
                                               cancelled = params["cancelled"],
                                               home_team_score = params["home_team_score"],
                                               away_team_score = params["away_team_score"],
                                               ref_id = params["ref_id"],
                                               game_kind = params["game_kind"])
            else:
                new_sports_event = SportsEvent(title = params["title"],
                                               start_date = params["start_date"],
                                               end_date = params["end_date"],
                                               league = params["league"],
                                               season = params["season"],
                                               home_team = params["home_team"],
                                               away_team = params["away_team"],
                                               completed = params["completed"],
                                               cancelled = params["cancelled"],
                                               home_team_score = params["home_team_score"],
                                               away_team_score = params["away_team_score"],
                                               ref_id = params["ref_id"],
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
            if "cancelled" in params:
                event.cancelled = params["cancelled"]
            if "home_team_score" in params:
                event.home_team_score = params["home_team_score"]
            if "away_team_score" in params:
                event.away_team_score = params["away_team_score"]
            if "league" in params:
                event.league = params["league"]
            if "season" in params:
                event.season = params["season"]
            if "home_team" in params:
                event.home_team = params["home_team"]
            if "away_team" in params:
                event.away_team = params["away_team"]
            if "ref_id" in params:
                event.ref_id = params["ref_id"]
            if "game_kind" in params:
                event.game_kind = params["game_kind"]

        event.put()
        return event
        
        

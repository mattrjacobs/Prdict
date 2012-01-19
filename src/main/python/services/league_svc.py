import logging
import simplejson as json

from google.appengine.ext import db

from models.league import League
from models.sport import Sport
from services.base_svc import BaseService

class LeagueService(BaseService):
    def get_model(self):
        return League

    def get_entry_list_name(self):
        return "leagues"

    @staticmethod
    def get_league_by_name(name):
        db_query = db.Query(League).filter("title =", name)
        result = db_query.fetch(1)
        if result and len(result) == 1:
            return result[0]
        else:
            return None

    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        description = self.get_json_str(parsed_body, "description")
        sport = self.get_sport_from_request(request, self.get_json_str(parsed_body,  "sport"))
        ref_id = self.get_json_str(parsed_body, "ref_id")

        return self.__create_param_map(title, description, sport, ref_id)

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        description = self.get_form_str(request, "description")
        sport = self.get_sport_from_request(request, request.get("sport"))

        ref_id = self.get_form_str(request, "ref_id")
        return self.__create_param_map(title, description, sport, ref_id)

    def __create_param_map(self, title, description, sport, ref_id):
        params = { }
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description
        if sport is not None:
            params["sport"] = sport
        if ref_id is not None:
            params["ref_id"] = ref_id
        else:
            params["ref_id"] = ""

        return params

    def validate_params(self, params):
        return League.validate_params(params)

    def validate_subset_params(self, league, params):
        return league.validate_subset_params(params)

    def create_entry_from_params(self, params):
        new_league = League(title = params["title"],
                            description = params["description"],
                            sport = params["sport"],
                            ref_id = params["ref_id"])
        new_league.put()
        return new_league

    def update_entry_from_params(self, league, params):
        if "title" in params:
            league.title = params["title"]
        if "description" in params:
            league.description = params["description"]
        if "sport" in params:
            league.sport = params["sport"]
        if "ref_id" in params:
            league.ref_id = params["ref_id"]
        return league

    def delete_entry_from_parent_in_txn(self, sport, league):
        league.sport = None
        return league
        

import logging
import simplejson as json

from google.appengine.ext import db

from models.league import League
from models.season import Season
from services.base_svc import BaseService

class SeasonService(BaseService):
    def get_model(self):
        return Season

    def get_entry_list_name(self):
        return "seasons"

    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        league = self.get_league_from_request(request, self.get_json_str(parsed_body,  "league"))
        return self.__create_param_map(title, league)

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        league = self.get_league_from_request(request, request.get("league"))
        return self.__create_param_map(title, league)

    def __create_param_map(self, title, league):
        params = { }
        if title is not None:
            params["title"] = title
        if league is not None:
            params["league"] = league
        return params

    def validate_params(self, params):
        return Season.validate_params(params)

    def validate_subset_params(self, season, params):
        return season.validate_subset_params(params)

    def create_entry_from_params(self, params):
        new_season = Season(title = params["title"],
                            league = params["league"])
        new_season.put()
        return new_season

    def update_entry_from_params(self, season, params):
        if "title" in params:
            season.title = params["title"]
        if "league" in params:
            season.league = params["league"]
        return season

    def delete_entry_from_parent_in_txn(self, league, season):
        season.league = None
        return season
        

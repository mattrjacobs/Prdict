import logging
import simplejson as json

from google.appengine.ext import db

from models.league import League
from models.team import Team
from services.base_svc import BaseService

class TeamService(BaseService):
    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        description = self.get_json_str(parsed_body, "description")
        location = self.get_json_str(parsed_body, "location")
        league = self.get_league_from_request(request, self.get_json_str(parsed_body,  "league"))

        return self.__create_param_map(title, description, location, league)

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        description = self.get_form_str(request, "description")
        location = self.get_form_str(request, "location")
        league = self.get_league_from_request(request, request.get("league"))

        return self.__create_param_map(title, description, location, league)

    def __create_param_map(self, title, description, location, league):
        params = { }
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description
        if location is not None:
            params["location"] = location
        if league is not None:
            params["league"] = league

        return params

    def validate_params(self, params):
        return Team.validate_params(params)

    def validate_subset_params(self, team, params):
        return team.validate_subset_params(params)

    def create_entry_from_params(self, params):
        new_team = Team(title = params["title"],
                        description = params["description"],
                        location = params["location"],
                        league = params["league"])
        new_team.put()
        return new_team

    def update_entry_from_params(self, team, params):
        if "title" in params:
            team.title = params["title"]
        if "description" in params:
            team.description = params["description"]
        if "location" in params:
            team.location = params["location"]
        if "league" in params:
            team.league = params["league"]
        return team

    def delete_entry_from_parent_in_txn(self, league, team):
        if team in league.teams:
            league.teams.remove(team)
            return league
        else:
            logging.debug("Attempting to remove team from league, but not a parent")


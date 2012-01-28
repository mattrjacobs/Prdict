import logging
import simplejson as json

from google.appengine.ext import db

from models.league import League
from models.team import Team
from services.base_svc import BaseService

class TeamService(BaseService):
    def get_model(self):
        return Team

    def get_entry_list_name(self):
        return "teams"

    def get_teams_by_league_name(self, league_name):
        query = db.GqlQuery("SELECT * FROM Team where league.name = :1 ORDER BY title", league_name)
        return query.fetch(100, 0)

    @staticmethod
    def get_team_by_league_and_team_name(league_key, team_name):
        query = db.GqlQuery("SELECT * From Team where league = :1 AND title = :2 ORDER BY location", league_key, team_name)
        team_list = query.fetch(1, 0)
        if len(team_list) == 1:
            return team_list[0]
        else:
            return None

    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        description = self.get_json_str(parsed_body, "description")
        location = self.get_json_str(parsed_body, "location")
        league = self.get_league_from_request(request, self.get_json_str(parsed_body,  "league"))
        ref_id = self.get_json_str(parsed_body, "ref_id")

        return self.__create_param_map(title, description, location,
                                       league, ref_id)

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        description = self.get_form_str(request, "description")
        location = self.get_form_str(request, "location")
        league = self.get_league_from_request(request, request.get("league"))
        ref_id = self.get_form_str(request, "ref_id")

        return self.__create_param_map(title, description, location,
                                       league, ref_id)

    def __create_param_map(self, title, description, location, league, ref_id):
        params = { }
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description
        if location is not None:
            params["location"] = location
        if league is not None:
            params["league"] = league
        if ref_id is not None:
            params["ref_id"] = ref_id
        else:
            params["ref_id"] = ""

        return params

    def validate_params(self, params):
        return Team.validate_params(params)

    def validate_subset_params(self, team, params):
        return team.validate_subset_params(params)

    def create_entry_from_params(self, params):
        new_team = Team(title = params["title"],
                        description = params["description"],
                        location = params["location"],
                        league = params["league"],
                        ref_id = params["ref_id"])

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
        if "ref_id" in params:
            team.ref_id = params["ref_id"]
        return team

    def delete_entry_from_parent_in_txn(self, league, team):
        if team in league.teams:
            league.teams.remove(team)
            return league
        else:
            logging.debug("Attempting to remove team from league, but not a parent")


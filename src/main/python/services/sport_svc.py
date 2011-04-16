import logging
import simplejson as json

from google.appengine.ext import db

from models.sport import Sport
from services.base_svc import BaseService

class SportService(BaseService):
    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        description = self.get_json_str(parsed_body, "description")

        return self.__create_param_map(title, description)

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        description = self.get_form_str(request, "description")

        return self.__create_param_map(title, description)

    def __create_param_map(self, title, description):
        params = { }
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description

        return params

    def validate_params(self, params):
        return Sport.validate_params(params)

    def validate_subset_params(self, sport, params):
        return sport.validate_subset_params(params)

    def create_entry_from_params(self, params):
        new_sport = Sport(title = params["title"],
                          description = params["description"])
        new_sport.put()
        return new_sport

    def update_entry_from_params(self, sport, params):
        if "title" in params:
            sport.title = params["title"]
        if "description" in params:
            sport.description = params["description"]
        return sport

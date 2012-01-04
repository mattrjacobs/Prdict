import logging
import simplejson as json

from google.appengine.ext import db

from models.sport import Sport
from services.base_svc import BaseService

class SportService(BaseService):
    def get_model(self):
        return Sport

    def get_entry_list_name(self):
        return "sports"

    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        title = self.get_json_str(parsed_body, "title")
        description = self.get_json_str(parsed_body, "description")
        ref_id = self.get_json_str(parsed_body, "ref_id")

        return self.__create_param_map(title, description, ref_id)

    def get_form_params(self, request):
        title = self.get_form_str(request, "title")
        description = self.get_form_str(request, "description")
        ref_id = self.get_form_str(request, "ref_id")

        return self.__create_param_map(title, description, ref_id)

    def __create_param_map(self, title, description, ref_id):
        params = { }
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description
        if ref_id is not None:
            params["ref_id"] = ref_id
        else:
            params["ref_id"] = ""

        return params

    def validate_params(self, params):
        return Sport.validate_params(params)

    def validate_subset_params(self, sport, params):
        return sport.validate_subset_params(params)

    def create_entry_from_params(self, params):
        new_sport = Sport(title = params["title"],
                          description = params["description"],
                          ref_id = params["ref_id"])

        new_sport.put()
        return new_sport

    def update_entry_from_params(self, sport, params):
        if "title" in params:
            sport.title = params["title"]
        if "description" in params:
            sport.description = params["description"]
        if "ref_id" in params:
            sport.ref_id = params["ref_id"]
        return sport

from abstract_model import AbstractModel

import logging
import simplejson as json

from google.appengine.ext import db

class SportEncoder(json.JSONEncoder):
    def default(self, sport):
        if not isinstance(sport, Sport):
            return

        return { 'title' : sport.title,
                 'description' : sport.description,
                 'link' : sport.relative_url,
                 'leagues' : "%s/leagues" % sport.relative_url,
                 'created' : sport.isoformat_created,
                 'updated' : sport.isoformat_updated }

class Sport(AbstractModel):
    @staticmethod
    def find_by_name(name):
        query = db.GqlQuery("SELECT * FROM Sport WHERE title = :1 LIMIT 1",
                            name)
        sport = query.fetch(1)
        if len(sport) > 0:
            return sport[0]
        else:
            return None

    @staticmethod
    def validate_params(params):
        return AbstractModel.validate_orig_params(params)

    @staticmethod
    def validate_subset_params(params):
        valid = True
        error_msgs = []
        if "title" in params:
            valid = valid and AbstractModel.validate_param(
                AbstractModel.validate_title(params["title"]),
                error_msgs)
        if "description" in params:
            valid = valid and AbstractModel.validate_param(
                AbstractModel.validate_description(params["description"]),
                error_msgs)

        if valid:
            return (True, None)
        else:
            return (False, ",".join(error_msgs))

    def get_leagues(self):
        query = db.GqlQuery("SELECT * FROM League WHERE sport = :1 AND ANCESTOR IS :1",
                            self)
        return query.fetch(100)
    leagues = property(get_leagues)
        
    def get_item_name(self):
        return "sport"
    item_name = property(get_item_name)

    def to_json(self):
        return SportEncoder(sort_keys=True).encode(self)

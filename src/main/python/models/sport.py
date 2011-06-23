from abstract_model import AbstractModel

import logging
import simplejson as json
import urllib

from google.appengine.ext import db

class SportEncoder(json.JSONEncoder):
    def default(self, sport):
        if not isinstance(sport, Sport):
            return

        return { 'title' : sport.title,
                 'description' : sport.description,
                 'ref_id' : sport.ref_id,
                 'link' : sport.relative_url,
                 'leagues' : "%s/leagues" % sport.relative_url,
                 'created' : sport.isoformat_created,
                 'updated' : sport.isoformat_updated }

class Sport(AbstractModel):
    #should be something like /api/sports/<key>
    @staticmethod
    def parse_sport_uri(sport_uri):
        uri_pieces = urllib.unquote(sport_uri).strip("/").split("/")
        try:
            if len(uri_pieces) == 3:
                if uri_pieces[0] != "api" or uri_pieces[1] != "sports":
                    return None
                sport_key = uri_pieces[2]
                return db.get(db.Key(encoded = sport_key))
            else:
                return None
        except db.BadKeyError:
            return None

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

    ref_id = db.StringProperty(required=False)

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

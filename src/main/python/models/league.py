from abstract_model import AbstractModel

import logging
import simplejson as json

from google.appengine.ext import db

from models.sport import Sport

class LeagueEncoder(json.JSONEncoder):
    def default(self, league):
        if not isinstance(league, League):
            return

        return { 'title' : league.title,
                 'description' : league.description,
                 'link' : league.relative_url,
                 'teams' : "%s/teams" % league.relative_url,
                 'sport' : league.sport.relative_url,
                 'created' : league.isoformat_created,
                 'updated' : league.isoformat_updated}

class League(AbstractModel):
    @staticmethod
    def find_by_name(name):
        query = db.GqlQuery("SELECT * FROM League WHERE title = :1 " +
                            "LIMIT 1", name)
        league = query.fetch(1)
        if len(league) > 0:
            return league[0]
        else:
            return None

    @staticmethod
    def validate_params(params):
        (are_orig_valid, orig_error_msg) = \
                         AbstractModel.validate_orig_params(params)
        error_msgs = []
        if "sport" in params:
            sport_valid = AbstractModel.validate_param(
                League.validate_sport(params["sport"]),
                error_msgs)
            if sport_valid:
                return (are_orig_valid, orig_error_msg)
            else:
                return (False, ",".join(orig_error_msg, "Sport is null"))
        else:
            return (False, ",".join(orig_error_msg, "Sport is missing"))

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
        if "sport" in params:
            valid = valid and AbstractModel.validate_param(
                League.validate_sport(params["sport"]),
                error_msgs)

        if valid:
            return (True, None)
        else:
            return (False, ",".join(error_msgs))

    @staticmethod
    def validate_sport(sport):
        if sport:
            return (True, None)
        else:
            return (False, "Sport is null")

    def get_teams(self):
        query = db.GqlQuery("SELECT * FROM Team WHERE league = :1",
                            self)
        query.ancestor(self)
        return query.fetch(100)
    teams = property(get_teams)

    def get_item_name(self):
        return "league"
    item_name = property(get_item_name)

    sport = db.ReferenceProperty(required=True, reference_class=Sport)

    def to_json(self):
        return LeagueEncoder(sort_keys=True).encode(self)


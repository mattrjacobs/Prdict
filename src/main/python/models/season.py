from abstract_model import AbstractModel

import logging
import simplejson as json
import urllib

from google.appengine.ext import db

from models.league import League

class SeasonEncoder(json.JSONEncoder):
    def default(self, season):
        if not isinstance(season, Season):
            return

        return { 'title' : season.title,
                 'self' : season.relative_url,
                 'league' : season.league.relative_url,
                 'created' : season.isoformat_created,
                 'updated' : season.isoformat_updated}

class Season(AbstractModel):
    #should be something like /api/leagues/<key>/seasons/<key>
    @staticmethod
    def parse_season_uri(season_uri):
        uri_pieces = urllib.unquote(season_uri).strip("/").split("/")
        try:
            if len(uri_pieces) == 5:
                if uri_pieces[0] != "api" or uri_pieces[1] != "leagues":
                    return None
                league_key = uri_pieces[2]
                league = db.get(db.Key(encoded = league_key))
                if uri_pieces[3] != "seasons":
                    return None
                season_key = uri_pieces[4]
                season = db.get(db.Key(encoded = season_key))
                return season
            else:
                return None
        except db.BadKeyError:
            return None
            
#    @staticmethod
#    def find_by_name(name):
#        query = db.GqlQuery("SELECT * FROM League WHERE title = :1 " +
#                            "LIMIT 1", name)
#        league = query.fetch(1)
#        if len(league) > 0:
#            return league[0]
#        else:
#            return None

    @staticmethod
    def validate_params(params):
        (are_orig_valid, orig_error_msg) = \
                         AbstractModel.validate_orig_params(params)
        if are_orig_valid:
            error_msgs = []
        else:
            error_msgs = [orig_error_msg]
        if "league" in params:
            league_valid = AbstractModel.validate_param(
                Season.validate_league(params["league"]), error_msgs)
            if league_valid:
                return (are_orig_valid, orig_error_msg)
            else:
                error_msgs.append("League is invalid")
                return (False, ",".join(error_msgs))
        else:
            error_msgs.append("League is missing")
            return (False, ",".join(error_msgs))

#    @staticmethod
#    def validate_subset_params(params):
#        valid = True
#        error_msgs = []
#        if "title" in params:
#            valid = valid and AbstractModel.validate_param(
#                AbstractModel.validate_title(params["title"]),
#                error_msgs)
#        if "description" in params:
#            valid = valid and AbstractModel.validate_param(
#                AbstractModel.validate_description(params["description"]),
#                error_msgs)
#        if "sport" in params:
#            valid = valid and AbstractModel.validate_param(
#                League.validate_sport(params["sport"]),
#                error_msgs)
#
#        if valid:
#            return (True, None)
#        else:
#            return (False, ",".join(error_msgs))

    @staticmethod
    def validate_league(league):
        if league:
            return (True, None)
        else:
            return (False, "League is null")

    #def get_teams(self):
    #    query = db.GqlQuery("SELECT * FROM Team WHERE league = :1 ORDER BY location",
    #                        self)
    #    return query.fetch(100)
    #teams = property(get_teams)

    def get_relative_url(self):
        return "/api/leagues/%s/seasons/%s" % (self.league.key(), self.key())
    relative_url = property(get_relative_url)

    def get_item_name(self):
        return "season"
    item_name = property(get_item_name)

    league = db.ReferenceProperty(required=True, reference_class=League)
    
    def to_json(self):
        return SeasonEncoder(sort_keys=True).encode(self)


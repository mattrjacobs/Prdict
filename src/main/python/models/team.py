from abstract_model import AbstractModel

import logging
import simplejson as json
import urllib

from google.appengine.ext import db

from models.league import League

class TeamEncoder(json.JSONEncoder):
    def default(self, team):
        if not isinstance(team, Team):
            return

        return { 'title' : team.title,
                 'description' : team.description,
                 'location' : team.location,
                 'logo_url' : team.logo_url,
                 'ref_id' : team.ref_id,
                 'self' : team.relative_url,
                 'league' : team.league.relative_url,
                 'created' : team.isoformat_created,
                 'updated' : team.isoformat_updated }

class Team(AbstractModel):
    league = db.ReferenceProperty(required=True, reference_class=League)
    location = db.StringProperty(required=True, multiline=False)
    #Make this required later
    logo_url = db.StringProperty(required=False, multiline=False)
    ref_id = db.StringProperty(required=False)

    #should be something like /api/teams/<key>
    @staticmethod
    def parse_team_uri(team_uri):
        uri_pieces = urllib.unquote(team_uri).strip("/").split("/")
        try:
            if len(uri_pieces) == 3:
                if uri_pieces[0] != "api" or uri_pieces[1] != "teams":
                    return None
                team_key = uri_pieces[2]
                return db.get(db.Key(encoded = team_key))
            else:
                return None
        except db.BadKeyError:
            return None
        
    @staticmethod
    def find_by_name(name, location, league):
        if not name:
            return None
        if not location and not league:
            query = db.GqlQuery("SELECT * FROM Team WHERE title = :1 LIMIT 1",
                                name)
        elif location and not league:
            query = db.GqlQuery("SELECT * FROM Team WHERE title = :1 AND location = :2 LIMIT 1", name, location)
        elif not location and league:
            query = db.GqlQuery("SELECT * FROM Team WHERE title = :1 AND league = :2 LIMIT 1", name, league)
        elif location and league:
            query = db.GqlQuery("SELECT * FROM Team WHERE title = :1 AND location = :2 AND league = :3", name, location, league)
        team = query.fetch(1)
        if len(team) > 0:
            return team[0]
        else:
            return None

    @staticmethod
    def validate_params(params):
        (are_orig_valid, orig_error_msg) = \
                         AbstractModel.validate_orig_params(params)
        league_ok = False
        if are_orig_valid:
            error_msgs = []
        else:
            error_msgs = [orig_error_msg]
        if "league" in params:
            league_valid = AbstractModel.validate_param(
                Team.validate_league(params["league"]),
                error_msgs)
            if league_valid:
                league_ok = True
        else:
            error_msgs.append("League is missing")

        location_ok = False
        if "location" in params:
            location_valid = AbstractModel.validate_param(
                Team.validate_location(params["location"]),
                error_msgs)
            if location_valid:
                location_ok = True
        else:
            error_msgs.append("Location is missing")

        if are_orig_valid and league_ok and location_ok:
            return (True, None)
        else:
            return (False, ",".join(error_msgs))

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
        if "league" in params:
            valid = valid and AbstractModel.validate_param(
                Team.validate_league(params["league"]),
                error_msgs)
        if "location" in params:
            valid = valid and AbstractModel.validate_param(
                Team.validate_location(params["location"]),
                error_msgs)

        if valid:
            return (True, None)
        else:
            return (False, ",".join(error_msgs))

    @staticmethod
    def validate_league(league):
        if league:
            return (True, None)
        else:
            return (False, "League is null")

    @staticmethod
    def validate_location(location):
        if not location:
            return (False, "Location is null")
        if len(location.strip()) == 0:
            return (False, "Location is empty")
        if (len(location) > 80):
            return (False, "Location exceeds 80 chars")
        return (True, None)

    def get_item_name(self):
        return "team"
    item_name = property(get_item_name)

    def to_json(self):
        return TeamEncoder(sort_keys = True).encode(self)

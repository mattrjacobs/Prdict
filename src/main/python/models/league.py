from abstract_model import AbstractModel

from google.appengine.ext import db

from models.sport import Sport

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

    def get_teams(self):
        query = db.GqlQuery("SELECT * FROM Team WHERE league = :1",
                            self)
        return query.fetch(100)
    teams = property(get_teams)

    def get_item_name(self):
        return "league"
    item_name = property(get_item_name)

    sport = db.ReferenceProperty(required=True,reference_class=Sport)


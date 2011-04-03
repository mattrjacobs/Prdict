from abstract_model import AbstractModel

from google.appengine.ext import db

from models.league import League

class Team(AbstractModel):
    league = db.ReferenceProperty(required=True,reference_class=League)
    location = db.StringProperty(required=True,multiline=False)

    def get_item_name(self):
        return "team"
    item_name = property(get_item_name)

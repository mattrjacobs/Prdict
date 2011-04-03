from abstract_model import AbstractModel

from google.appengine.ext import db

from models.sport import Sport

class League(AbstractModel):
    sport = db.ReferenceProperty(required=True,reference_class=Sport)

    def get_item_name(self):
        return "league"
    item_name = property(get_item_name)

from abstract_model import AbstractModel

from google.appengine.ext import db

import logging

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
        
    def get_item_name(self):
        return "sport"
    item_name = property(get_item_name)

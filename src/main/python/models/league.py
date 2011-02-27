from abstract_model import AbstractModel

class League(AbstractModel):
    def get_item_name(self):
        return "league"
    item_name = property(get_item_name)

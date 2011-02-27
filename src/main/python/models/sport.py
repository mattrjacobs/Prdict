from abstract_model import AbstractModel

class Sport(AbstractModel):
    def get_item_name(self):
        return "sport"
    item_name = property(get_item_name)

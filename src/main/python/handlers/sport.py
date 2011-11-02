"""Handles a request for a sport"""
import httplib

from handlers.auth import BaseAuthorizationHandler
from handlers.entry import EntryHandler
from models.sport import Sport
from services.sport_svc import SportService

class SportHandler(EntryHandler, BaseAuthorizationHandler):
    """Handles a request for an sport resource.
    EntryHandler has logic for HTTP operations
    BaseAuthorizationHandler has logic for authorization."""
    def __init__(self):
        self.sport_svc = SportService()

    def render_html(self, entry, msg=None):
        """Renders an HTML Sport"""
        current_user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(current_user, None)
        self.render_template("sport.html",
                             { 'msg': msg,
                               'current_user' : current_user,
                               'can_write' : can_write,
                               'entry' : entry})

    def get_svc(self):
        return self.sport_svc

    def get_html(self, entry):
        return "sport.html"

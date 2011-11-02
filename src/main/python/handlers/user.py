"""Handles request for a user resource"""
import httplib

from handlers.auth import UserAuthorizationHandler, http_basic_auth
from handlers.entry import EntryHandler

class UserHandler(EntryHandler, UserAuthorizationHandler):
    """Handles an HTTP request for a PrdictUser resource
    EntryHandler handles request parsing
    UserAuthorizationHandler handles authorization logic"""
    def render_html(self, entry, msg=None):
        current_user = self.get_prdict_user()
        self.render_template(self.get_html(entry),
                             { 'msg' : msg,
                               'current_user' : current_user,
                               'user' : entry })

    def post(self, key):
        self.allow_overloaded_post_of_delete(key)

    #For now, can't update users - this will change
    @http_basic_auth
    def put(self, user, key):
        return self.response.set_status(httplib.METHOD_NOT_ALLOWED)

    def get_html(self, entry):
        return "user.html"

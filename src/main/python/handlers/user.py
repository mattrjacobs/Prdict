"""HAndles request for a user resource"""
import httplib

from handlers.auth import UserAuthorizationHandler
from handlers.entry import EntryHandler

class UserHandler(EntryHandler, UserAuthorizationHandler):
    """Handles an HTTP request for a PrdictUser resource
    EntryHandler handles request parsing
    UserAuthorizationHandler handles authorization logic"""
    def render_html(self, entry, msg=None):
        current_user = self.get_prdict_user()
        self.render_template('user.html', { 'msg' : msg,
                                            'current_user' : current_user,
                                            'user' : entry })

    def render_atom(self, entry):
        self.render_template('xml/user_atom.xml',
                             { 'user' : entry,
                               'base_url' : self.baseurl() } )

    def render_json(self, entry):
        self.render_template('json/user_json.xml',
                             { 'user' : entry,
                               'base_url' : self.baseurl() } )
        
    def post(self, key):
        self.allow_overloaded_post_of_delete(key)

    #For now, can't update users - this will change
    def put(self, key):
        return self.response.set_status(httplib.METHOD_NOT_ALLOWED)

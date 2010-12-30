"""Handles a request for a user's friends resource"""
import httplib
import logging

from google.appengine.api import users

from handlers.auth import UserAuthorizationHandler
from handlers.feed import FeedHandler
from models import prdict_user

class UserFriendsHandler(FeedHandler, UserAuthorizationHandler):
    """Handles a request for a user's friends resource
    FeedHandler has logic on request processing
    UserAuthorizationHandler has logic for authorization"""
    def get_entries(self, parent, limit = 25, offset = 0):
        """Get friends of the user subject to limit/offset parameters"""
        if parent:
            return [prdict_user.lookup_user(u)
                    for u in parent.friends[offset:offset+limit]]
        else:
            return []

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg = None):
        self.render_template('friends.html',
                             { 'current_user' : self.get_prdict_user(),
                               'user' : parent,
                               'friends' : entries,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'msg' : msg})

    def render_atom(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        self.render_template('xml/friends_atom.xml',
                             { 'user' : parent,
                               'friends' : entries,
                               'self_link' : self.request.url,
                               'base_url' : self.baseurl(),
                               'prev_link' : prev_link,
                               'next_link' : next_link})

    def render_json(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        self.render_template('json/friends_json.json',
                             { 'user' : parent,
                               'friends' : entries })
    def is_post_data_valid(self, parent):
        """Checks if request parameters contain a valid user to add"""
        email = self.request.get("email")
        (is_valid, error_message) = prdict_user.PrdictUser.validate_email(email)
        if not is_valid:
            return (False, error_message)
        if parent.email == email:
            return (False, "Can not add yourself as a friend")
        already_registered = prdict_user.PrdictUser.user_registered(email)
        if not already_registered:
            return (False, "User is not currently registered")
        return (True, None)

    def handle_post(self, parent):
        """Respond to a POST that we know contains a valid friend to add"""
        user_to_insert = users.User(self.request.get("email"))
        if user_to_insert not in parent.friends:
            self.add_to_friends(parent, user_to_insert)
            msg = "New friend added"
        else:
            self.response.set_status(httplib.FOUND)
            msg = "Already friends with %s" % user_to_insert
        friends_location = self.baseurl() + parent.get_relative_url() + "/friends"
        self.set_header('Content-Location', friends_location)
        self.render_html(parent, self.get_entries(parent = parent), msg = msg)

    def add_to_friends(self, parent, user_to_insert):
        """Add a friend to the parent user and update HTTP status"""
        parent.friends.append(user_to_insert)
        parent.put()
        self.response.set_status(httplib.CREATED)


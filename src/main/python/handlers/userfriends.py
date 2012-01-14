"""Handles a request for a user's friends resource"""
import httplib
import logging
import simplejson as json

from google.appengine.api import users

from handlers.auth import UserAuthorizationHandler
from handlers.feed import FeedHandler
from models import prdict_user
from utils.constants import Constants

class UserFriendsHandler(FeedHandler, UserAuthorizationHandler):
    """Handles a request for a user's friends resource
    FeedHandler has logic on request processing
    UserAuthorizationHandler has logic for authorization"""

    def get_parent_name(self):
        return "user"

    def is_post_data_valid(self, parent):
        """Checks if request parameters contain a valid user to add"""
        email = self.get_email_from_request()
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
        email = self.get_email_from_request()
        user_to_insert = users.User(email)
        if user_to_insert not in parent.friends:
            self.add_to_friends(parent, user_to_insert)
            msg = "New friend added"
        else:
            self.response.set_status(httplib.FOUND)
            msg = "Already friends with %s" % user_to_insert
        friends_location = self.baseurl() + parent.get_relative_url() + "/friends"
        self.set_header('Content-Location', friends_location)
        friends = self.get_entries(parent = parent, query = None)
        self.render_html(parent, friends, msg = msg)

    def add_to_friends(self, parent, user_to_insert):
        """Add a friend to the parent user and update HTTP status"""
        parent.friends.append(user_to_insert)
        parent.put()
        self.response.set_status(httplib.CREATED)

    def get_email_from_request(self):
        email = None
        content_type = self.get_header('Content-Type')
        if content_type == Constants.FORM_ENCODING:
            email = self.request.get("email")
        elif content_type == Constants.JSON_ENCODING:
            parsed_body = json.loads(self.request.body)
            if 'email' in parsed_body:
                email = parsed_body['email']
        return email

    def get_max_results_allowed(self):
        return 100

    def get_default_max_results(self):
        return 50

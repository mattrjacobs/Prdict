"""Handles requests for the resource of all users"""
import httplib
import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from handlers.handler import AbstractHandler
from models import prdict_user
from utils.constants import Constants

class UsersHandler(AbstractHandler):
    """Handles requests for the resource of all users."""
    def get(self):
        """Renders a template for adding a new user"""
        user = self.get_prdict_user()
        content_type = self.get_read_content_type()
        #for now, only permit admin users to access
        if not users.is_current_user_admin():
            self.set_403(content_type)
            return None

        self.render_template('users.html', {'current_user' : user})

    def render_json(self):
        json_list = [json.loads(user.to_json()) for user in \
                     self.get_all_users()]
        self.render_string(json.dumps(json_list))

    def post(self):
        """Attempts to respond to a POST by adding a new user"""
        #for now, only permit admin users to create
        current_user = self.get_prdict_user()
        content_type = self.get_write_content_type()
        if not users.is_current_user_admin():
            self.set_403(content_type)
            return None
        if content_type == "form":
            email = self.request.get("email")
            username = self.request.get("username")
        elif content_type == "json":
            parsed_user = json.loads(self.request.body)
            if 'email' in parsed_user:
                email = parsed_user['email']
            else:
                email = ''
            if 'username' in parsed_user:
                username = parsed_user['username']
            else:
                username = ''
        else:
            msg = "Must POST as Form-Encoded or JSON"
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template('users.html',
                                        { 'msg': msg,
                                          'current_user' : current_user})
        (is_valid, error_message) = prdict_user.PrdictUser.validate_params(username, email)
        if not is_valid:
            return self.set_400("users.html", content_type, error_message)
        email_user = users.User(email)
        if prdict_user.PrdictUser.user_registered(email):
            user = prdict_user.lookup_user(email_user)
            self.response.set_status(httplib.FOUND)
        else:
            try:
                user = self.create_user(username, email_user)
            except CapabilityDisabledError:
                self.handle_transient_error(content_type)
                return
        user_url = "%s/%s" % (self.request.url, user.key())
        self.response.headers['Content-Location'] = user_url
        if content_type == "json":
            self.render_string(user.to_json())
        else:
            self.render_template('user.html', { 'user' : user,
                                                'current_user' : current_user})

    def create_user(self, username, email_user):
        """Adds a new user to datastore and sets HTTP status"""
        user = prdict_user.PrdictUser(username = username, user = email_user)
        user.put()
        self.response.set_status(httplib.CREATED)
        return user

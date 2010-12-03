"""Handles requests for the resource of all users"""
import httplib
import logging

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
        #for now, only permit admin users to access
        if not users.is_current_user_admin():
            self.set_403()
            return None
        self.render_template('users.html')

    def post(self):
        """Attempts to respond to a POST by adding a new user"""
        #for now, only permit admin users to create
        user = self.get_prdict_user()
        if not users.is_current_user_admin():
            self.set_403()
            return None
        if self.get_header('Content-Type') != Constants.FORM_ENCODING:
            msg = "Must POST in %s format." % Constants.FORM_ENCODING
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template('users.html', { 'msg': msg })
        email = self.request.get("email")
        username = self.request.get("username")
        (is_valid, error_message) = prdict_user.PrdictUser.validate_params(username, email)
        if not is_valid:
            return self.__bad_request_template(error_message)
        email_user = users.User(email)
        if prdict_user.PrdictUser.user_registered(email):
            user = prdict_user.lookup_user(email_user)
            self.response.set_status(httplib.FOUND)
        else:
            try:
                user = self.create_user(username, email_user)
            except CapabilityDisabledError:
                self.handle_transient_error()
                return
        user_url = "%s/%s" % (self.request.url, user.key())
        self.response.headers['Content-Location'] = user_url
        self.render_template('user.html', { 'user' : user })

    def create_user(self, username, email_user):
        """Adds a new user to datastore and sets HTTP status"""
        user = prdict_user.PrdictUser(username = username, user = email_user)
        user.put()
        self.response.set_status(httplib.CREATED)
        return user

    def __bad_request_template(self, message):
        """Returns an HTML template explaining why user add failed"""
        self.response.set_status(httplib.BAD_REQUEST)
        return self.render_template('users.html', { 'msg' : message })

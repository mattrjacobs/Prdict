"""Handles authorization for Prdict resources:
Users/Events"""
from google.appengine.api import users
import logging

class AuthorizationHandler:
    """Base class for providing authorization service"""

    def __init__(self):
        pass

    def is_user_authorized_to_read(self, user, entry):
        """Return a boolean stating whether the given user is authorized
        to read the given entry"""
        raise Exception("Must be overridden by subclasses")
    
    def is_user_authorized_to_write(self, user, entry):
        """Return a boolean stating whether the given user is authorized
        to write the given entry"""
        raise Exception("Must be overridden by subclasses")

class EventChatAuthorizationHandler(AuthorizationHandler):
    """Authorization for event chat resource"""
    def __init__(self):
        AuthorizationHandler.__init__(self)

    def is_user_authorized_to_read(self, prdict_user, event):
        return prdict_user

    def is_user_authorized_to_write(self, prdict_user, event):
        return prdict_user

class FriendsAuthorizationHandler(AuthorizationHandler):
    """Authorization for user friends resource"""
    def __init__(self):
        AuthorizationHandler.__init__(self)

    def is_user_authorized_to_read(self, prdict_user, entry):
        return prdict_user and (entry.key() == prdict_user.key() or \
                                prdict_user.user in entry.friends or \
                                users.is_current_user_admin())

    def is_user_authorized_to_write(self, prdict_user, entry):
        return prdict_user and (entry.key() == prdict_user.key() or \
                                users.is_current_user_admin())

class BaseAuthorizationHandler(AuthorizationHandler):
    """Base authorization for a resource"""
    def __init__(self):
        AuthorizationHandler.__init__(self)

    def is_user_authorized_to_read(self, prdict_user, item):
        return True

    def is_user_authorized_to_write(self, prdict_user, item):
        return users.is_current_user_admin()

class UserAuthorizationHandler(AuthorizationHandler):
    """Authorization for user resource"""
    def __init__(self):
        AuthorizationHandler.__init__(self)

    def is_user_authorized_to_read(self, prdict_user, entry):
        return prdict_user or users.is_current_user_admin()

    def is_user_authorized_to_write(self, prdict_user, entry):
        return prdict_user and (entry.key() == prdict_user.key() or \
                                users.is_current_user_admin())


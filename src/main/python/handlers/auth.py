"""Handles authorization for Prdict resources:
Users/Events"""
from google.appengine.api import users
import functools
import logging
import os

def http_basic_auth(method):
    import base64
    import gauth
    import httplib
    from models import prdict_user

    MY_APP_NAME = "prdictapi" 

    @functools.wraps(method)
    def http_basic_auth_deco(self, *args):
        cookie_user = users.get_current_user()
        logging.error("COOKIE USER : %s" % cookie_user)
        user = None
        if not cookie_user:
            basic_auth = self.request.headers.get("Authorization")
            if not basic_auth:
                user = None
            else:
                username, password = '', ''
                try:
                    user_info = base64.decodestring(basic_auth[6:])
                    username, password = user_info.split(":")
                except:
                    user = None
                cookie = None
                try:
                    is_dev = self.is_dev_host()
                    http_host = os.environ["HTTP_HOST"]
                    if is_dev:
                        cookie = gauth.do_auth(MY_APP_NAME, http_host, username, password, True, True)
                    else:
                        cookie = gauth.do_auth(MY_APP_NAME, http_host, username, password, False)
                    # Give ASCID cookie to client
                    self.response.headers['Set-Cookie'] = cookie
                    self.response.set_status(httplib.UNAUTHORIZED)
                    return
                except gauth.AuthError, e:
                    logging.error("Got a failed login attempt for Google Accounts %s" % username)
                    user = None
        elif 'Authorization' in self.request.headers:
            assert 'USER_ID' in os.environ
            del self.request.headers['Authorization']
            del os.environ['HTTP_AUTHORIZATION']
        if cookie_user:
            user = prdict_user.lookup_user(cookie_user)
            if user:
                assert isinstance(user, prdict_user.PrdictUser), "%r" % user
        return method(self, user, *args)
    return http_basic_auth_deco

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


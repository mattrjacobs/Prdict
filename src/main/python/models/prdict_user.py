import dateutil
import logging
import re
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import db

class PrdictUserEncoder(json.JSONEncoder):
    def default(self, user):
        if not isinstance(user, PrdictUser):
            return

        return { 'email' : user.email,
                 'username' : user.username,
                 'self' : user.relative_url,
                 'friends' : "%s/friends" % user.relative_url,
                 'created' : user.isoformat_created,
                 'updated' : user.isoformat_updated }

class PrdictUser(db.Model):

    user = db.UserProperty(required=True)
    username = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    friends = db.ListProperty(users.User)

    #add events user is interested in

    @staticmethod
    def validate_email(email):
        """Given an email, can a valid User be constructed?
        Return a (is_valid, error_message) tuple"""
        if not email or not email.strip():
            return (False, "Must specify a non-empty 'email' parameter.")
        if len(email) > 80:
            return (False, "Email length must be less than or equal to 80 chars")
        if not re.match(r'.*@.*\..*', email):
            return (False, "Email parameter must connect an at and dot")
        user = users.User(email)
        if not user:
            return (False, "Email parameter must be valid.")
        return (True, None)

    @staticmethod
    def validate_params(username, email):
        (is_email_valid, error_message) = PrdictUser.validate_email(email)
        if not is_email_valid:
            return (False, error_message)
        lookup_username = db.GqlQuery(
            "SELECT * FROM PrdictUser WHERE username = :1", username)
        if not username or not email.strip():
            return (False, "Must specify a non-empty 'username' parameter.")
        if len(username.split()) > 1:
            return (False, "Username must not contain whitespace")
        if lookup_username.get() is not None:
            return (False, "Username already taken")
        if len(username) < 4:
            return (False, "Username length must be greater than or equal to 4 chars")
        if len(username) > 20:
            return (False, "Username length must be less than or equal to 20 chars")
        return (True, None)

    @staticmethod
    def user_registered(email):
        """Given an email, is that user registered already?"""
        user = users.User(email)
        if not user: return False
        db_user = lookup_user(user)
        if not db_user: return False
        return True

    def get_isoformat_created(self):
        return "%sZ" % (self.created.isoformat(),)
    isoformat_created = property(get_isoformat_created)
    
    def get_isoformat_updated(self):
        return "%sZ" % (self.updated.isoformat(),)
    isoformat_updated = property(get_isoformat_updated)

    def get_email(self):
        return self.user.email()
    email = property(get_email)

    def get_etag(self):
        return "\"%s-%s\"" % (dateutil.unix_timestamp(self.created),
                              dateutil.unix_timestamp(self.updated))
    etag = property(get_etag)

    def get_relative_url(self):
        return "/api/users/%s" % (self.key(),)
    relative_url = property(get_relative_url)

    def to_json(self):
        return PrdictUserEncoder(sort_keys=True).encode(self)

def lookup_user(cookie_user):
    """Given a user instantiated from a cookie, determine if that user is
    already in the datastore - If so, return it.  If not, return None."""
    user_lookup = db.GqlQuery("SELECT * FROM PrdictUser WHERE user = :1", cookie_user)
    return user_lookup.get()

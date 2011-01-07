from google.appengine.ext import db

from datetime import datetime

import build
import dateutil
from event import Event
from prdict_user import PrdictUser

class Message(db.Model):
    content = db.StringProperty(required=True,multiline=False)
    created = db.DateTimeProperty(auto_now_add=True)
    author = db.ReferenceProperty(required=True, reference_class=PrdictUser)
    event = db.ReferenceProperty(required=True, reference_class=Event)

    @staticmethod
    def validate_params(content):
        """Given message content, can a valid Message be constructed?
        Return a (is_valid, error_message) tuple"""
        if not content or not content.strip():
            return (False, "Must specify a non-empty 'content' parameter.")
        if len(content) > 140:
            return (False, "Content length must be 140 chars or less.")
        return (True, None)

    def get_etag(self):
        return "\"%s-%s\"" % (dateutil.unix_timestamp(self.created),
                                 build.build_number)
    etag = property(get_etag)

    def get_isoformat_created(self):
        return "%sZ" % (self.created.isoformat(),)
    isoformat_created = property(get_isoformat_created)
    
    def get_relative_url(self):
        return "/api/messages/%s" % (self.key(),)
    relative_url = property(get_relative_url)    

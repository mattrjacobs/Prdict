from google.appengine.ext import db

from datetime import datetime
import simplejson as json

import build
import dateutil
from event import Event
from prdict_user import PrdictUser

class MessageEncoder(json.JSONEncoder):
    def default(self, msg):
        if not isinstance(msg, Message):
            return

        return { 'content' : msg.content,
                 'author' : msg.author.relative_url,
                 'event' : msg.event.relative_url,
                 'created' : msg.isoformat_created }

class Message(db.Model):
    DATE_FORMAT = "%I:%M:%S"

    content = db.StringProperty(required=True,multiline=False)
    created = db.DateTimeProperty(auto_now_add=True)
    author = db.ReferenceProperty(required=True, reference_class=PrdictUser)
    event = db.ReferenceProperty(required=True, reference_class=Event)

    @staticmethod
    def validate_params(params):
        """Given message content, can a valid Message be constructed?
        Return a (is_valid, error_message) tuple"""
        error_msgs = []
        if "content" in params:
            content = params["content"]
            if not content or not content.strip():
                error_msgs.append("Must specify a non-empty 'content' parameter.")
            if len(content) > 140:
                error_msgs.append("Content length must be 140 chars or less.")
        else:
            error_msgs.append("Content is required")
        if not "created_date" in params:
            error_msgs.append("Created date is required")
        if not "author" in params:
            error_msgs.append("Author is required")
        if not "event" in params:
            error_msgs.append("Event is required")
        if len(error_msgs) > 0:
            return (False, ",".join(error_msgs))
        else:
            return (True, None)
            

    def get_etag(self):
        return "\"%s-%s\"" % (dateutil.unix_timestamp(self.created),
                                 build.build_number)
    etag = property(get_etag)

    def get_isoformat_created(self):
        return "%sZ" % (self.created.isoformat(),)
    isoformat_created = property(get_isoformat_created)

    def get_created_nice(self):
        return self.created.strftime(Message.DATE_FORMAT)
    created_nice = property(get_created_nice)
    
    def get_relative_url(self):
        return "/api/messages/%s" % (self.key(),)
    relative_url = property(get_relative_url)    

    def to_json(self):
        return JsonEncoder(sort_keys=True).encode(self)

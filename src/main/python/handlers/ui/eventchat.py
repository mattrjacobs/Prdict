"""Handles a request for an event's chat"""
from datetime import datetime
import hashlib
import httplib
import logging
import random

from django.utils import simplejson
from google.appengine.api import channel
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import EventChatAuthorizationHandler
from handlers.feed import FeedHandler
from models.message import Message
from models import prdict_user
from services.message_svc import MessageService

class EventChatUiHandler(FeedHandler, EventChatAuthorizationHandler):
    def __init__(self):
        self.message_svc = MessageService()

    """Handles a request for an event chat resource
    FeedHandler has logic on request processing
    EventChatAuthorizationHandler has logic for authorization"""
    def get_entries(self, parent, limit = 1000, offset = 0):
        """Get chat for the event subject to limit/offset parameters"""
        if parent:
            query = db.GqlQuery("SELECT * FROM Message WHERE event = :1 ORDER BY created DESC",
                                parent.key())
            return query.fetch(limit, offset)
        else:
            return []

    def render_html(self, parent, entries, prev_link=None, next_link=None,
                    msg = None, user = None):
        if user:
            user_id = user.user.user_id()
        else:
            user_id = random.randint(1000, 99999)
        client_id = user_id
        cache_key = "listeners-%s" % str(parent.key())
        rand = random.randint(1000, 9999)
        channel_id = "%s-%s-%s" % (client_id, str(parent.key()), rand)
        hasher = hashlib.sha1()
        hasher.update(channel_id)
        hashed_channel_id = hasher.hexdigest()
        token = channel.create_channel(hashed_channel_id)
        current_listeners = memcache.get(cache_key)
        if current_listeners:
            if not channel_id in current_listeners:
                current_listeners.append(hashed_channel_id)
        else:
            current_listeners = [hashed_channel_id]

        memcache.set(cache_key, current_listeners)
        channel_msg = self.get_channel_message(None)
        for listener in current_listeners:
            channel.send_message(listener, channel_msg)

        self.render_template('ui_eventchat.html',
                             { 'current_user' : user,
                               'token' : token,
                               'event' : parent,
                               'event_key' : str(parent.key()),
                               'messages' : entries,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'build' : self.get_build_number(),
                               'msg' : msg})

    def render_atom(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        raise RuntimeError("ATOM not valid for UI Eventchat")

    def render_json(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        raise RuntimeError("JSON not valid for UI EventChat")

    def get_channel_message(self, user):
        """Create a message stating some user just signed in"""
        logging.error("USER : %s" % user)
        if user:
            logging.error("USER : %s" % user.username)
        if user:
            username = user.username
        else:
            username = "Anonymous"
        chat_message = { 'author' : 'Admin',
                         'message' : '%s joined' % username,
                         'message_time' : datetime.utcnow().strftime(Message.DATE_FORMAT) }
        return simplejson.dumps(chat_message)
                         
    def get_svc(self):
        return self.message_svc

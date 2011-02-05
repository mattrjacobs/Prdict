"""Handles a request for an event's chat"""
import httplib
import logging
import random

from google.appengine.api import channel
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from handlers.auth import EventChatAuthorizationHandler
from handlers.feed import FeedHandler
from models.message import Message
from models import prdict_user

class EventChatUiHandler(FeedHandler, EventChatAuthorizationHandler):
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
                    msg = None):
        client_id = self.get_prdict_user().user.user_id()
        cache_key = "listeners-%s" % str(parent.key())
        rand = random.randint(1000, 9999)
        channel_id = "%s-%s-%s" % (client_id, str(parent.key()), rand)
        token = channel.create_channel(channel_id)
        current_listeners = memcache.get(cache_key)
        if current_listeners:
            if not channel_id in current_listeners:
                current_listeners.append(channel_id)
        else:
            current_listeners = [channel_id]

        memcache.set(cache_key, current_listeners)

        self.render_template('ui_eventchat.html',
                             { 'current_user' : self.get_prdict_user(),
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


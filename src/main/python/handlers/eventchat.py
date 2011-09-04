"""Handles a request for an event's chat"""
import httplib
import logging

from django.utils import simplejson
from google.appengine.api import channel
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from handlers.auth import EventChatAuthorizationHandler
from handlers.feed import FeedHandler
from models.message import Message
from models import prdict_user
from services.message_svc import MessageService

class EventChatHandler(FeedHandler, EventChatAuthorizationHandler):
    def __init__(self):
        self.message_svc = MessageService()
        self.html = "eventchat.html"
        self.entry_html = "message.html"

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
         self.render_template('eventchat.html',
                             { 'current_user' : user,
                               'event' : parent,
                               'event_key' : str(parent.key()),
                               'messages' : entries,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'msg' : msg})

    def render_atom(self, parent, entries, prev_link=None, next_link=None, msg = None):
        raise "Not implemented yet"

    def handle_post_success(self, parent, new_entry):
        channel_msg = self.get_channel_message(new_entry)
        cache_key = "listeners-%s" % str(parent.key())
        listeners = memcache.get(cache_key)
        if listeners:
            for listener in listeners:
                channel.send_message(listener, channel_msg)


    def get_channel_message(self, message):
        chat_message = { 'author' : message.author.username,
                         'author_link' : message.author.relative_url,
                         'message' : message.content,
                         'message_time' : message.created_nice }
        return simplejson.dumps(chat_message)
            
    def create_chat(self, event):
        message_to_add = Message(content = self.request.get("content"),
                                 author = self.get_prdict_user(),
                                 event = event)
        message_to_add.put()
        return message_to_add

    def get_parent_name(self):
        return "event"

    def get_entries_name(self):
        return "messages"

    def get_svc(self):
        return self.message_svc

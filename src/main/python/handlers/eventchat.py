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

class EventChatHandler(FeedHandler, EventChatAuthorizationHandler):
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
         self.render_template('eventchat.html',
                             { 'current_user' : self.get_prdict_user(),
                               'event' : parent,
                               'event_key' : str(parent.key()),
                               'messages' : entries,
                               'self_link' : self.request.url,
                               'prev_link' : prev_link,
                               'next_link' : next_link,
                               'msg' : msg})

    def render_atom(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        self.render_template('xml/eventchat_atom.xml',
                             { 'event' : parent,
                               'messages' : entries,
                               'self_link' : self.request.url,
                               'base_url' : self.baseurl(),
                               'prev_link' : prev_link,
                               'next_link' : next_link})

    def render_json(self, parent, entries, prev_link=None, next_link=None,
                    msg=None):
        self.render_template('json/eventchat_json.json',
                             { 'event' : parent,
                               'messages' : entries })

    def is_post_data_valid(self, parent):
        """Checks if request parameters contain a valid message to add"""
        content = self.request.get("content")
        return Message.validate_params(content)

    def handle_post(self, parent):
        """Respond to a POST that we know contains a valid message to add"""
        try:
            message_to_add = self.create_chat(parent)
        except CapabilityDisabledError:
            self.handle_transient_error()
            return
        msg = "Added message"
        chat_location = self.baseurl() + parent.get_relative_url() + "/chat"

        self.response.set_status(httplib.CREATED)
        self.set_header('Content-Location', chat_location)
        self.render_html(parent, self.get_entries(parent = parent), msg = msg)

        channel_msg = self.get_channel_message(message_to_add)
        cache_key = "listeners-%s" % str(parent.key())
        listeners = memcache.get(cache_key)
        if listeners:
            for listener in listeners:
                channel_id = listener + str(parent.key())
                channel.send_message(channel_id, channel_msg)

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


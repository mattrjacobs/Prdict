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

    def get_max_results_allowed(self):
        return 1000

    def get_default_max_results(self):
        return 100

    def get_svc(self):
        return self.message_svc

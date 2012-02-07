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
        self.html = 'ui_eventchat.html'

    def create_param_map(self, user, parent, entries, pagination_params, total_count, can_write, now):
        if user:
            user_id = user.user.user_id()
        else:
            user_id = random.randint(1000, 99999)
        client_id = user_id
        rand = random.randint(1000, 9999)
        channel_id = "%s-%s-%s" % (client_id, str(parent.key()), rand)
        hasher = hashlib.sha1()
        hasher.update(channel_id)
        hashed_channel_id = hasher.hexdigest()
        token = channel.create_channel(hashed_channel_id)

        cache_key = "listeners-%s" % str(parent.key())
        current_listeners = memcache.get(cache_key)
        if current_listeners:
            if not channel_id in current_listeners:
                current_listeners.append(hashed_channel_id)
        else:
            current_listeners = [ hashed_channel_id ]

        memcache.set(cache_key, current_listeners)
        channel_msg = self.get_channel_message(user)
        for listener in current_listeners:
            channel.send_message(listener, channel_msg)

        return { 'current_user'   : user,
                 'start-index'    : pagination_params[0],
                 'max-results'    : pagination_params[1],
                 'total-results'  : total_count,
                 'can_write'      : can_write,
                 'now'            : now,
                 'token'          : token,
                 self.get_parent_name() : parent,
                 self.get_svc().get_entry_list_name() : entries
            }

    def get_max_results_allowed(self):
        return 1000
    
    def get_default_max_results(self):
        return 50

    def get_parent_name(self):
        return "event"

    def get_channel_message(self, user):
        """Create a message stating some user just signed in"""
        if user:
            username = user.username
        else:
            username = "Anonymous"
        chat_message = { 'author' : 'Admin',
                         'content' : '%s joined' % username,
                         'timestamp' : datetime.utcnow().strftime(Message.DATE_FORMAT) }
        return simplejson.dumps(chat_message)
                         
    def get_svc(self):
        return MessageService()

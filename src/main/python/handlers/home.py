from handlers.handler import AbstractHandler

import datetime
import logging

from google.appengine.api import memcache
from google.appengine.ext import db

from auth import http_basic_auth
from models import prdict_user

class HomeHandler(AbstractHandler):
    @http_basic_auth
    def get(self, user):
        self.render_template("home.html",
                             { 'current_user' : user })

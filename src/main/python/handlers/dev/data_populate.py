from handlers.handler import AbstractHandler

from datetime import datetime
from datetime import timedelta
import logging
import os
import random

from google.appengine.api import users
from google.appengine.ext import db

from models import event
from models import prdict_user

class DevDataPopulateHandler(AbstractHandler):
    def get(self):
        new_users = []
        new_events = []

        if "SERVER_NAME" in os.environ.keys():
            server_name = os.environ["SERVER_NAME"]
            if server_name == "localhost":
                for i in range(0, 10):
                    user = prdict_user.PrdictUser(username="user_%d" % i,
                                                  user=users.User("user_%d@testprdict.com" % i))
                    user.friends = []
                    for j in range(0, i):
                        friend_email = "user_%d@testprdict.com" % j
                        user.friends.append(users.User(friend_email))
                    user.put()
                    new_users.append(user)

                    rnd_for_start = random.randint(0, 100) - 50
                    rnd_for_end = random.randint(0, 100)
                    now = datetime.now()
                    start_date = now + timedelta(days = rnd_for_start)
                    end_date = start_date + timedelta(hours = rnd_for_end)
                    new_event = event.Event(title = "Event_%d" % i,
                                            description = "Description_%d" % i,
                                            start_date = start_date,
                                            end_date = end_date)
                    new_event.put()
                    new_events.append(new_event)

        self.render_template("devPopulate.html",
                             { 'users' : new_users,
                               'events' : new_events })

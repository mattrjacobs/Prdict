#!/usr/bin/env python
from cStringIO import StringIO
from datetime import datetime
import logging
import mox
import os
import simplejson as json
import unittest
import wsgiref

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import user_service_stub
from google.appengine.api import users
from google.appengine.api.memcache import memcache_stub
from google.appengine.ext.webapp import Request
from google.appengine.ext.webapp import Response 

from models.event import Event
from models.league import League
from models.message import Message
from models.season import Season
from models.sport import Sport
from models.sports_event import SportsEvent
from models.team import Team
from models.prdict_user import PrdictUser

APP_ID = 'Prdict API'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@prdict.com'
SERVER_NAME = 'localhost'
SERVER_PORT = '8080'
URL_SCHEME = 'http'

DATASTORE_STUB_NAME = 'datastore_v3'
MEMCACHE_STUB_NAME = "memcache"
USER_SERVICE_STUB_NAME = 'user'

class BaseServiceTest(unittest.TestCase):
    def setUp(self):
        os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
        os.environ['APPLICATION_ID'] = APP_ID
        os.environ['SERVER_NAME'] = SERVER_NAME
        os.environ['SERVER_PORT'] = SERVER_PORT
        os.environ['wsgi.url_scheme'] = URL_SCHEME
        os.environ['USER_IS_ADMIN'] = "0"

        self.stub_req = self.req("", "GET")

        self.original_apiproxy = apiproxy_stub_map.apiproxy
        self.clear_datastore()
        self.clear_memcache()
        self.clear_userstore()

        self.email = LOGGED_IN_USER
        self.username = "test"
        self.friend_email = "friend@prdict.com"
        self.friend_username = "friend"
        self.non_friend_email = "non_friend@prdict.com"
        self.non_friend_username = "non_friend"
        self.admin_email = "admin@prdict.com"
        self.admin_username = "admin"

        self.friend_user = self._create_user(self.friend_username, self.friend_email)
        self.non_friend_user = self._create_user(self.non_friend_username, self.non_friend_email)
        self.admin_user = self._create_user(self.admin_username, self.admin_email) 
        self.user = self._create_user(self.username, self.email, [users.User(self.friend_email)])
        self.user_key = str(self.user.key())

        self.sport = self._create_sport("Sport 1", "")
        self.sport_key = str(self.sport.key())

        self.league = self._create_league("League 1", "League 1 Desc", self.sport)
        self.league_key = str(self.league.key())

        self.season = self._create_season("2011", self.league)
        self.season_key = str(self.season.key())

        self.team_1 = self._create_team("Team 1", "Team 1 Desc",
                                        self.league, "Team 1 Loc")
        self.team_1_key = str(self.team_1.key())

        self.team_2 = self._create_team("Team 2", "Team 2 Desc",
                                        self.league, "Team 2 Loc")
        self.team_2_key = str(self.team_2.key())

        self.event = self._create_event("Event 1", "Event 1 Desc", "2012-1-1 08:00:00", "2012-1-1 11:00:00")
        self.event_key = str(self.event.key())

        self.sports_event = self._create_sports_event(
            "Sports Event 1", "Sports Event Desc 1", "2012-1-1 09:00:00",
            "2012-1-1 12:00:00", self.team_1, self.team_2, True, 80, 67,
            "Regular Season", self.league, self.season)
        self.sports_event_key = str(self.sports_event.key())

        self.message_1 = self._create_message("This is a message posted by user", self.user, self.event)
        self.message_1_key = str(self.message_1.key())
        self.message_2 = self._create_message("This is a message posted by friend", self.friend_user, self.event)
        self.message_2_key = str(self.message_2.key())

    def tearDown(self):
        apiproxy_stub_map.apiproxy = self.original_apiproxy

    def define_impl(self):
        raise "Not implemented"

    def clear_datastore(self):
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        stub = datastore_file_stub.DatastoreFileStub(APP_ID, None,  None)
        apiproxy_stub_map.apiproxy.RegisterStub(DATASTORE_STUB_NAME, stub)

    def clear_memcache(self):
        apiproxy_stub_map.apiproxy.RegisterStub(MEMCACHE_STUB_NAME, memcache_stub.MemcacheServiceStub())

    def clear_userstore(self):
        apiproxy_stub_map.apiproxy.RegisterStub(USER_SERVICE_STUB_NAME, user_service_stub.UserServiceStub())

    def req(self, body, method):
        req = Request({'wsgi.url_scheme' : URL_SCHEME,
                       'wsgi.input' : StringIO(body),
                       'SERVER_NAME' : SERVER_NAME,
                       'SERVER_PORT' : SERVER_PORT})
        req.body = body
        req.method = method
        return req

    def reqWithQuery(self, body, method, query_params):
        req = Request({'wsgi.url_scheme' : URL_SCHEME,
                       'wsgi.input' : StringIO(body),
                       'SERVER_NAME' : SERVER_NAME,
                       'SERVER_PORT' : SERVER_PORT,
                       'QUERY_STRING' : query_params })
        req.body = body
        req.method = method
        return req

    def reqWithPath(self, body, method, path):
        req = Request({'wsgi.url_scheme' : URL_SCHEME,
                       'wsgi.input' : StringIO(body),
                       'SERVER_NAME' : SERVER_NAME,
                       'SERVER_PORT' : SERVER_PORT,
                       'PATH_INFO' : path })
        req.body = body
        req.method = method
        return req

    def set_user(self, email, is_admin):
        os.environ["USER_EMAIL"] = email
        if is_admin:
            os.environ["USER_IS_ADMIN"] = "1"
        else:
            os.environ["USER_IS_ADMIN"] = "0"

    def remove_user(self):
        del os.environ["USER_EMAIL"]

    def _create_user(self, name, email, friends = []):
        user = PrdictUser(username = name, user = users.User(email), friends = friends)
        user_key = str(user.put())
        return user
    
    def _create_sport(self, title, description):
        sport = Sport(title = title, description = description)
        sport_key = str(sport.put())
        return sport

    def _create_league(self, title, description, sport):
        league = League(title = title, description = description,
                        sport = sport)
        league_key = str(league.put())
        return league

    def _create_season(self, title, league):
        season = Season(title = title, league = league)
        season.put()
        return season

    def _create_team(self, title, description, league, location):
        team = Team(title = title, description = description, league =
                    league, location = location)
        team_key = str(team.put())
        return team

    def _create_event(self, title, description, start_date_str, end_date_str):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        event = Event(title = title, description = description,
                      start_date = start_date, end_date = end_date)
        event_key = str(event.put())
        return event

    def _create_sports_event(self, title, description, start_date_str,
                             end_date_str, home_team, away_team, completed,
                             home_team_score, away_team_score, game_kind,
                             league, season):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        event = SportsEvent(title = title, description = description,
                            home_team = home_team, away_team = away_team,
                            completed = completed, home_team_score = \
                            home_team_score, away_team_score = away_team_score,
                            game_kind = game_kind, start_date = start_date,
                            end_date = end_date, league = league, season = season)
        event_key = str(event.put())
        return event

    def _create_message(self, content, author, event):
        message = Message(content = content, author = author, event = event)
        message_key = str(message.put())
        return message

    def expect_auth(self, value):
        self.mock_auth_handler.is_user_authorized_for_entry(mox.Func(self.SameUserKey),
                                                            mox.Func(self.SameEntryKey)).AndReturn(value)

    def SameEntryKey(self, entry):
        return entry.key() == self.entry.key()
        
    def SameUserKey(self, user):
        return user.key() == self.user.key()

    def JsonPostResponseOk(self, responseJson):
        readJson = json.loads(responseJson)
        return readJson['status'] == 'ok'
    
    def JsonPostResponseError(self, responseJson):
        readJson = json.loads(responseJson)
        return readJson['status'] == 'error' and \
               len(readJson['message']) > 0

#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.league import LeagueHandler 
from models.league import League
from utils.constants import Constants

class TestLeagueHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'title' : 'New League',
                              'description' : 'New League Description'}

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(LeagueHandler)
        self.impl = MockLeagueHandler(self.mock_handler)
        
    def JsonFromLeague(self, leagueJson):
        readJson = json.loads(leagueJson)
        title_ok = self.league.title == readJson['title']
        desc_ok = self.league.description == readJson['description']
        link_ok = "/api/leagues/%s" % self.league.key() == readJson['link']
        team_ok = "/api/leagues/%s/teams" % self.league.key() == \
                  readJson['teams']
        sport_ok = "/api/sports/%s" % self.league.sport.key() == \
                   readJson['sport']

        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0
        
        return title_ok and desc_ok and link_ok and team_ok and \
               sport_ok and created_ok and updated_ok

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.mock_handler.render_template("league.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.league_key)
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("league.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.league_key)
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("league.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.league_key)
        self.mox.VerifyAll()        

    def testGetJsonWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_string(mox.Func(self.JsonFromLeague))
        self.mox.ReplayAll()

        self.impl.get(self.league_key)
        self.mox.VerifyAll()

class MockLeagueHandler(LeagueHandler):
    def __init__(self, handler):
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

    def render_string(self, s):
        self.handler.render_string(s)

if __name__ == '__main__':
    unittest.main()

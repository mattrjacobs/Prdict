#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.team import TeamHandler 
from models.team import Team
from utils.constants import Constants

class TestTeamHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'title' : 'New Team',
                              'description' : 'New Team Description',
                              'location' : 'New Team Location'}

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(TeamHandler)
        self.impl = MockTeamHandler(self.mock_handler)

    def JsonFromTeam(self, teamJson):
        readJson = json.loads(teamJson)
        title_ok = self.team_1.title == readJson['title']
        desc_ok = self.team_1.description == readJson['description']
        location_ok = self.team_1.location == readJson['location']
        link_ok = "/api/teams/%s" % self.team_1.key() == readJson['link']
        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0
        
        return title_ok and desc_ok and location_ok and link_ok and \
               created_ok and updated_ok
    
    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.mock_handler.render_template("team.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.team_1_key)
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("team.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.team_1_key)
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("team.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.team_1_key)
        self.mox.VerifyAll()

    def testGetJsonWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_string(mox.Func(self.JsonFromTeam))
        self.mox.ReplayAll()

        self.impl.get(self.team_1_key)
        self.mox.VerifyAll()        

class MockTeamHandler(TeamHandler):
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

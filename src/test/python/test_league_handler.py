#!/usr/bin/env python

import logging
import mox
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

class MockLeagueHandler(LeagueHandler):
    def __init__(self, handler):
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

import logging
import mox
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.leagues import LeaguesHandler 
from models.league import League
from utils.constants import Constants

class TestLeaguesHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'title' : 'New League',
                              'description' : 'New League Description'}

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(LeaguesHandler)
        self.impl = MockLeaguesHandler(self.mock_handler)

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()        

    def testPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidContentType(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = "invalid content type"
        self.impl.response.set_status(415)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostMissingTitle(self):
        invalid_params = { 'description' : 'New League Description'}

        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostEmptyTitle(self):
        invalid_params = { 'title' : '',
                           'description' : 'New League Description'}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostMissingDesc(self):
        invalid_params = { 'title' : 'New League'}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_template("league.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedLeague(url, {'title' : 'New League', 'description' : ''})
        self.mox.VerifyAll()

    def testPostEmptyDesc(self):
        invalid_params = { 'title' : 'New League',
                           'description' : ''}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_template("league.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedLeague(url, {'title' : 'New League', 'description' : ''})
        self.mox.VerifyAll()

    def testPostValidPostParamGAEReadOnly(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_item") 

        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.create_item(("New League", "New League Description")).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.render_template("503.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertFalse(self.impl.response.headers.has_key("Content-Location"))
        self.mox.VerifyAll()

    def testPostValidPostParamAsNonAdmin(self):
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostValidPostParamAsAdminCreateNewLeague(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(201)
        self.mock_handler.render_template("league.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedLeague(url, self.valid_params)
        self.mox.VerifyAll()

    def verifyReturnedLeague(self, url, expected_params):
        league_key = url[url.rindex("/") + 1:]
        returned_league = db.get(db.Key(encoded = league_key))
        self.assertEquals(returned_league.title, expected_params['title'])
        self.assertEquals(returned_league.description, expected_params['description'])
        
class MockLeaguesHandler(LeaguesHandler):
    def __init__(self, handler):
        LeaguesHandler.__init__(self)
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

if __name__ == '__main__':
    unittest.main()

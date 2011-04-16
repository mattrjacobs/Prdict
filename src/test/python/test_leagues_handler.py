#!/usr/bin/env python

import logging
import mox
import simplejson as json
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
                              'description' : 'New League Description',
                              'sport' : self.sport.title}

        self.league_2 = self._create_league("League 2", "", self.sport)
        self.league_3 = self._create_league("League 3", "", self.sport)

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(LeaguesHandler)
        self.impl = MockLeaguesHandler(self.mock_handler)

    def ValidParamTuple(self, arg):
        (title, desc, sport) = arg
        return title == "New League" and desc == "New League Description" and str(sport.key()) == str(self.sport_key)
    

    def JsonFromLeagues(self, leagueJson):
        readJson = json.loads(leagueJson)
        league_1 = filter(lambda league: league['title'] == "League 1",
                          readJson)[0]
        league_2 = filter(lambda league: league['title'] == "League 2",
                          readJson)[0]
        league_3 = filter(lambda league: league['title'] == "League 3",
                          readJson)[0]

        league_1_ok = league_1["description"] == "League 1 Desc" and \
                      league_1["link"] == \
                      "/api/leagues/%s" % self.league.key() and \
                      league_1["teams"] == \
                      "/api/leagues/%s/teams" % self.league.key() and \
                      league_1["sport"] == \
                      "/api/sports/%s" % self.sport.key() and \
                      len(league_1["updated"]) > 0 and \
                      len(league_1["created"]) > 0
        league_2_ok = league_2["description"] == "" and \
                      league_2["link"] == \
                      "/api/leagues/%s" % self.league_2.key() and \
                      league_2["teams"] == \
                      "/api/leagues/%s/teams" % self.league_2.key() and \
                      league_2["sport"] == \
                      "/api/sports/%s" % self.sport.key() and \
                      len(league_2["updated"]) > 0 and \
                      len(league_2["created"]) > 0
        league_3_ok = league_3["description"] == "" and \
                      league_3["link"] == \
                      "/api/leagues/%s" % self.league_3.key() and \
                      league_3["teams"] == \
                      "/api/leagues/%s/teams" % self.league_3.key() and \
                      league_3["sport"] == \
                      "/api/sports/%s" % self.sport.key() and \
                      len(league_3["updated"]) > 0 and \
                      len(league_3["created"]) > 0

        return league_1_ok and league_2_ok and league_3_ok

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

    def testJsonGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.render_string(mox.Func(self.JsonFromLeagues))
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testFormPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.request = self.req(json.dumps(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
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

    def testFormPostMissingTitle(self):
        invalid_params = { 'description' : 'New League Description',
                           'sport' : self.sport.title }

        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testJsonPostMissingTitle(self):
        invalid_params = { 'description' : 'New League Description',
                           'sport' : self.sport.title }

        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostEmptyTitle(self):
        invalid_params = { 'title' : '',
                           'description' : 'New League Description',
                           'sport' : self.sport.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostEmptyTitle(self):
        invalid_params = { 'title' : '',
                           'description' : 'New League Description',
                           'sport' : self.sport.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostMissingDesc(self):
        invalid_params = { 'title' : 'New League',
                           'sport' : self.sport.title }
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

    def testJsonPostMissingDesc(self):
        invalid_params = { 'title' : 'New League',
                           'sport' : self.sport.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseOk))
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedLeague(url, {'title' : 'New League', 'description' : ''})
        self.mox.VerifyAll()

    def testFormPostEmptyDesc(self):
        invalid_params = { 'title' : 'New League',
                           'description' : '',
                           'sport' : self.sport.title }
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

    def testJsonPostEmptyDesc(self):
        invalid_params = { 'title' : 'New League',
                           'description' : '',
                           'sport' : self.sport.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseOk))
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedLeague(url, {'title' : 'New League', 'description' : ''})
        self.mox.VerifyAll()

    def testFormPostMissingSport(self):
        invalid_params = { 'title' : 'New League',
                           'description' : 'New League Description' }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testJsonPostMissingSport(self):
        invalid_params = { 'title' : 'New League',
                           'description' : 'New League Description' }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostEmptySport(self):
        invalid_params = { 'title' : 'New League',
                           'description' : 'New League Description',
                           'sport' : '' }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testJsonPostEmptySport(self):
        invalid_params = { 'title' : 'New League',
                           'description' : 'New League Description',
                           'sport' : '' }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostInvalidSport(self):
        invalid_params = { 'title' : 'New League',
                           'description' : 'New League Description',
                           'sport' : "not-a-sport" }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("leagues.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testJsonPostInvalidSport(self):
        invalid_params = { 'title' : 'New League',
                           'description' : 'New League Description',
                           'sport' : "not-a-sport" }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostValidPostParamGAEReadOnly(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_item") 

        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.create_item(mox.Func(self.ValidParamTuple)).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.render_template("errors/503.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertFalse(self.impl.response.headers.has_key("Content-Location"))
        self.mox.VerifyAll()

    def testJsonPostValidPostParamGAEReadOnly(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_item") 

        self.impl.request = self.req(json.dumps(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.create_item(mox.Func(self.ValidParamTuple)).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.assertFalse(self.impl.response.headers.has_key("Content-Location"))
        self.mox.VerifyAll()

    def testFormPostValidPostParamAsNonAdmin(self):
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostValidPostParamAsNonAdmin(self):
        self.impl.request = self.req(json.dumps(self.valid_params), "POST")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.response.set_status(403)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostValidPostParamAsAdminCreateNewLeague(self):
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

    def testJsonPostValidPostParamAsAdminCreateNewLeague(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(json.dumps(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.response.set_status(201)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseOk))
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
        self.assertEquals(str(returned_league.sport.key()), self.sport_key)
        
class MockLeaguesHandler(LeaguesHandler):
    def __init__(self, handler):
        LeaguesHandler.__init__(self)
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

    def render_string(self, s):
        self.handler.render_string(s)

if __name__ == '__main__':
    unittest.main()

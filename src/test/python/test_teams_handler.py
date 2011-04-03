#!/usr/bin/env python

import logging
import mox
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.teams import TeamsHandler 
from models.team import Team
from utils.constants import Constants

class TestTeamsHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'title' : 'New Team',
                              'description' : 'New Team Description',
                              'location' : 'New Team Location',
                              'league' : self.league.title}

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(TeamsHandler)
        self.impl = MockTeamsHandler(self.mock_handler)

    def ValidParamTuple(self, arg):
        (title, desc, league, location) = arg
        return title == "New Team" and \
               desc == "New Team Description" and \
               location == "New Team Location" and \
               str(league.key()) == str(self.league_key)
    

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
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
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostMissingTitle(self):
        invalid_params = { 'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'league' : self.league.title }

        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostEmptyTitle(self):
        invalid_params = { 'title' : '',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'league' : self.league.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostMissingDesc(self):
        invalid_params = { 'title' : 'New Team',
                           'location' : 'New Team Location',
                           'league' : self.league.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_template("team.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedTeam(url, {'title' : 'New Team',
                                      'description' : '',
                                      'location' : 'New Team Location'})
        self.mox.VerifyAll()

    def testPostEmptyDesc(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : '',
                           'location' : 'New Team Location',
                           'league' : self.league.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_template("team.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedTeam(url, {'title' : 'New Team',
                                      'description' : '',
                                      'location' : 'New Team Location'})
        self.mox.VerifyAll()

    def testPostMissingLocation(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'league' : self.league.title }

        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostEmptyLocation(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : '',
                           'league' : self.league.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostMissingLeague(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location'}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostEmptyLeague(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'sport' : '' }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostInvalidLeague(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'league' : "not-a-league" }
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testPostValidPostParamGAEReadOnly(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_item") 

        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.create_item(mox.Func(self.ValidParamTuple)).AndRaise(CapabilityDisabledError)
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

    def testPostValidPostParamAsAdminCreateNewTeam(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(201)
        self.mock_handler.render_template("team.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedTeam(url, self.valid_params)
        self.mox.VerifyAll()
        
    def verifyReturnedTeam(self, url, expected_params):
        team_key = url[url.rindex("/") + 1:]
        returned_team = db.get(db.Key(encoded = team_key))
        self.assertEquals(returned_team.title, expected_params['title'])
        self.assertEquals(returned_team.description,
                          expected_params['description'])
        self.assertEquals(returned_team.location, expected_params['location'])
        self.assertEquals(str(returned_team.league.key()), self.league_key)
        
class MockTeamsHandler(TeamsHandler):
    def __init__(self, handler):
        TeamsHandler.__init__(self)
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

import logging
import mox
import simplejson as json
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

        self.team_3 = self._create_team("Team 3", "", self.league, "Team 3 Loc")

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(TeamsHandler)
        self.impl = MockTeamsHandler(self.mock_handler)

    def JsonFromTeams(self, teamsJson):
        readJson = json.loads(teamsJson)
        team_1 = filter(lambda team: team['title'] == "Team 1", readJson)[0]
        team_2 = filter(lambda team: team['title'] == "Team 2", readJson)[0]
        team_3 = filter(lambda team: team['title'] == "Team 3", readJson)[0]

        team_1_ok = team_1['description'] == "Team 1 Desc" and \
                    team_1['link'] == "/api/teams/%s" % self.team_1.key() and \
                    team_1['league'] == \
                    "/api/leagues/%s" % self.league_key and \
                    team_1['location'] == "Team 1 Loc" and \
                    len(team_1["updated"]) > 0 and \
                    len(team_1["created"]) > 0

        team_2_ok = team_2['description'] == "Team 2 Desc" and \
                    team_2['link'] == "/api/teams/%s" % self.team_2.key() and \
                    team_2['league'] == \
                    "/api/leagues/%s" % self.league_key and \
                    team_2['location'] == "Team 2 Loc" and \
                    len(team_2["updated"]) > 0 and \
                    len(team_2["created"]) > 0

        team_3_ok = team_3['description'] == "" and \
                    team_3['link'] == "/api/teams/%s" % self.team_3.key() and \
                    team_3['league'] == \
                    "/api/leagues/%s" % self.league_key and \
                    team_3['location'] == "Team 3 Loc" and \
                    len(team_3["updated"]) > 0 and \
                    len(team_3["created"]) > 0
        
        return team_1_ok and team_2_ok and team_3_ok              

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

    def testJsonGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.render_string(mox.Func(self.JsonFromTeams))
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
        self.mock_handler.render_template("teams.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostMissingTitle(self):
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

    def testJsonPostMissingTitle(self):
        invalid_params = { 'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'league' : self.league.title }

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

    def testJsonPostEmptyTitle(self):
        invalid_params = { 'title' : '',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'league' : self.league.title }
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

    def testJsonPostMissingDesc(self):
        invalid_params = { 'title' : 'New Team',
                           'location' : 'New Team Location',
                           'league' : self.league.title }
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
        self.verifyReturnedTeam(url, {'title' : 'New Team',
                                      'description' : '',
                                      'location' : 'New Team Location'})
        self.mox.VerifyAll()

    def testFormPostEmptyDesc(self):
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

    def testJsonPostEmptyDesc(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : '',
                           'location' : 'New Team Location',
                           'league' : self.league.title }
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
        self.verifyReturnedTeam(url, {'title' : 'New Team',
                                      'description' : '',
                                      'location' : 'New Team Location'})
        self.mox.VerifyAll()

    def testFormPostMissingLocation(self):
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

    def testJsonPostMissingLocation(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'league' : self.league.title }

        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostEmptyLocation(self):
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

    def testJsonPostEmptyLocation(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : '',
                           'league' : self.league.title }
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostMissingLeague(self):
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

    def testJsonPostMissingLeague(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location'}
        self.set_user(self.username, True)
        self.impl.request = self.req(json.dumps(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testFormPostEmptyLeague(self):
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

    def testJsonPostEmptyLeague(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location',
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

    def testFormPostInvalidLeague(self):
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

    def testJsonPostInvalidLeague(self):
        invalid_params = { 'title' : 'New Team',
                           'description' : 'New Team Description',
                           'location' : 'New Team Location',
                           'league' : "not-a-league" }
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

    def testFormPostValidPostParamAsAdminCreateNewTeam(self):
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

    def testJsonPostValidPostParamAsAdminCreateNewTeam(self):
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

    def render_string(self, s):
        self.handler.render_string(s)

if __name__ == '__main__':
    unittest.main()

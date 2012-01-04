#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.list import ListHandler 
from models.abstract_model import AbstractModel
from services.base_svc import BaseService
from utils.constants import Constants

class TestListHandler(BaseMockHandlerTest):
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
        self.mock_handler = self.mox.CreateMock(ListHandler)
        self.mock_svc = self.mox.CreateMock(BaseService)
        self.impl = MockListHandler(self.mock_handler, self.mock_svc)
        self.mock_entry = self.mox.CreateMock(AbstractModel)

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
    

    def testHtmlGetNoUser(self):
        self.remove_user()
        self.mock_svc.get_count(None).AndReturn(3)
        self.mock_svc.get_entries((0, 5), None).AndReturn([])
        self.mock_handler.render_template("list.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testHtmlGetWithNonAdminUser(self):
        self.mock_svc.get_count(None).AndReturn(3)
        self.mock_svc.get_entries((0, 5), None).AndReturn([])
        self.mock_handler.render_template("list.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testHtmlGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_svc.get_count(None).AndReturn(3)
        self.mock_svc.get_entries((0, 5), None).AndReturn([])
        self.mock_handler.render_template("list.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()        

    def testJsonGetWithNoUser(self):
        self.remove_user()
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_svc.get_count(None).AndReturn(3)
        self.mock_svc.get_entries((0, 5), None).AndReturn([])
        self.mock_svc.get_entry_list_name().AndReturn("items")
        # DO ASSERT ON RETURNED JSON
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testJsonGetWithNonAdminUser(self):
        self.set_user(self.username, False)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_svc.get_count(None).AndReturn(3)
        self.mock_svc.get_entries((0, 5), None).AndReturn([])
        self.mock_svc.get_entry_list_name().AndReturn("items")
        # DO ASSERT ON RETURNED JSON
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testJsonGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_svc.get_count(None).AndReturn(3)
        self.mock_svc.get_entries((0, 5), None).AndReturn([])
        self.mock_svc.get_entry_list_name().AndReturn("items")
        # DO ASSERT ON RETURNED JSON
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testHtmlGetWithRefIdQueryParam(self):
        self.set_user(self.username, False)
        self.impl.request = self.reqWithQuery("", "GET", "q=refId:item-id")
        self.mock_svc.get_count(["refId", "item-id"]).AndReturn(1)
        self.mock_svc.get_entries((0, 5), ["refId", "item-id"]).AndReturn([])
        # DO ASSERT ON RETURNED JSON
        self.mock_handler.render_template("list.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testJsonGetWithRefIdQueryParam(self):
        self.set_user(self.username, False)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json&q=refId:item-id")
        self.mock_svc.get_count(["refId", "item-id"]).AndReturn(1)
        self.mock_svc.get_entries((0, 5), ["refId", "item-id"]).AndReturn([])
        self.mock_svc.get_entry_list_name().AndReturn("items")
        # DO ASSERT ON RETURNED JSON
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    #UNIT TESTS FOR PAGINATION

    def testFormPostWithNoUser(self):
        self.remove_user()
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostWithNoUser(self):
        self.remove_user()
        self.impl.request = self.req(json.dumps(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidContentType(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = "invalid content type"
        self.mock_svc.create_entry(self.impl.request, "unknown").AndReturn((False, False, False, "invalid content type", None))
        self.impl.response.set_status(415)
        self.mock_handler.render_template("list.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidFormParams(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.mock_svc.create_entry(self.impl.request, "form").AndReturn((True, False, False, "invalid params", None))
        self.impl.response.set_status(400)
        self.mock_handler.render_template("list.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidJsonParams(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.mock_svc.create_entry(self.impl.request, "json").AndReturn((True, False, False, "invalid params", None))
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostDbWriteFailedForm(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.mock_svc.create_entry(self.impl.request, "form").AndReturn((True,
        True, False, "DB write failed", None))
        self.impl.response.set_status(503)
        self.mock_handler.render_template("503.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostDbWriteFailedJson(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.mock_svc.create_entry(self.impl.request, "json").AndReturn((True,
        True, False, "Db write failed", None))
        self.impl.response.set_status(503)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostSucceededForm(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.mock_svc.create_entry(self.impl.request, "form").AndReturn((True,
        True, True, None, self.mock_entry))
        self.mock_entry.key().AndReturn("key")
        self.impl.response.set_status(201)
        self.mock_handler.render_template("entry.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        url = self.impl.response.headers["Content-Location"]
        self.assertEquals(url, "%s/%s" % (self.impl.request.url, "key"))
        self.mox.VerifyAll()

    def testPostSucceededJson(self):
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.mock_svc.create_entry(self.impl.request, "json").AndReturn((True,
        True, True, None, self.mock_entry))
        self.mock_entry.key().AndReturn("key")
        self.impl.response.set_status(201)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseOk))
        self.mox.ReplayAll()

        self.impl.post()
        url = self.impl.response.headers["Content-Location"]
        self.assertEquals(url, "%s/%s" % (self.impl.request.url, "key"))
        self.mox.VerifyAll()        
        
class MockListHandler(ListHandler):
    def __init__(self, handler, svc):
        ListHandler.__init__(self)
        self.handler = handler
        self.svc = svc

    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

    def render_string(self, s):
        self.handler.render_string(s)

    def get_svc(self):
        return self.svc

    def get_max_results_allowed(self):
        return 10

    def get_default_max_results(self):
        return 5
    
if __name__ == '__main__':
    unittest.main()

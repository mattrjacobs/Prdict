#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.auth import BaseAuthorizationHandler
from handlers.feed import FeedHandler 
from models.abstract_model import AbstractModel
from services.base_svc import BaseService
from utils.constants import Constants

class TestFeedHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.parent_key = self.league_key

        self.valid_params = { 'title' : 'New Team Title',
                              'location' : 'New Team Location',
                              'league' : self.league.relative_url }

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(FeedHandler)
        self.mock_svc = self.mox.CreateMock(BaseService)
        self.impl = MockFeedHandler(self.mock_handler, self.mock_svc)
        self.mock_entry = self.mox.CreateMock(AbstractModel)

    def testHtmlGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.mock_handler.get_entries(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg()).AndReturn([self.team_1, self.team_2])
        self.mock_handler.render_html(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.parent_key)
        self.mox.VerifyAll()

    def testHtmlGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.get_entries(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg()).AndReturn([self.team_1, self.team_2])
        self.mock_handler.render_html(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.parent_key)
        self.mox.VerifyAll()

    def testHtmlGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.admin_user)
        self.mock_handler.get_entries(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg()).AndReturn([self.team_1, self.team_2])
        self.mock_handler.render_html(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.parent_key)
        self.mox.VerifyAll()        

    def testJsonGetWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_entries(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg()).AndReturn([self.team_1, self.team_2])
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.parent_key)
        self.mox.VerifyAll()

    def testJsonGetWithNonAdminUser(self):
        self.set_user(self.username, False)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_entries(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg()).AndReturn([self.team_1, self.team_2])
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.parent_key)
        self.mox.VerifyAll()

    def testJsonGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.admin_user)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_entries(mox.Func(self.SameLeagueKey), mox.IgnoreArg(),
                                      mox.IgnoreArg()).AndReturn([self.team_1, self.team_2])
        self.mock_handler.render_string(mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.parent_key)
        self.mox.VerifyAll()

    def testFormPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testJsonPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.impl.request = self.req(json.dumps(self.valid_params), "POST")
        self.impl.request.headers["Accept"] = Constants.JSON_ENCODING
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testPostInvalidContentType(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.admin_user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = "invalid content type"
        self.mock_svc.create_entry(self.impl.request, "unknown").AndReturn((False, False, False, "invalid content type", None))
        self.impl.response.set_status(415)
        self.mock_handler.render_template("parent.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testPostInvalidFormParams(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode({'bad_param' : 'foo'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.mock_svc.create_entry(self.impl.request, "form").AndReturn((True, False, False, "invalid params", None))
        self.impl.response.set_status(400)
        self.mock_handler.render_template("parent.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testPostInvalidJsonParams(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(json.dumps({'bad_param' : 'foo'}), "POST")
        self.impl.request.headers["Accept"] = Constants.JSON_ENCODING
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.mock_svc.create_entry(self.impl.request, "json").AndReturn((True, False, False, "invalid params", None))
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testPostDbWriteFailedForm(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.mock_svc.create_entry(self.impl.request, "form").AndReturn((True, True, False, "DB write failed", None))
        self.impl.response.set_status(503)
        self.mock_handler.render_template("503.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testPostDbWriteFailedJson(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.admin_user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.mock_svc.create_entry(self.impl.request, "json").AndReturn((True, True, False, "Db write failed", None))
        self.impl.response.set_status(503)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        self.mox.VerifyAll()

    def testPostSucceededForm(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.admin_user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.mock_svc.create_entry(self.impl.request, "form").AndReturn((True, True, True, None, self.mock_entry))
        self.mock_entry.key().AndReturn("key")
        self.impl.response.set_status(201)
        self.mock_handler.handle_post_success(mox.Func(self.SameLeagueKey), self.mock_entry)
        self.mock_handler.render_template("entry.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        url = self.impl.response.headers["Content-Location"]
        self.assertEquals(url, "%s/%s" % (self.impl.request.url, "key"))
        self.mox.VerifyAll()

    def testPostSucceededJson(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.admin_user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.mock_svc.create_entry(self.impl.request, "json").AndReturn((True, True, True, None, self.mock_entry))
        self.mock_entry.key().AndReturn("key")
        self.impl.response.set_status(201)
        self.mock_handler.handle_post_success(mox.Func(self.SameLeagueKey), self.mock_entry)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseOk))
        self.mox.ReplayAll()

        self.impl.post(self.parent_key)
        url = self.impl.response.headers["Content-Location"]
        self.assertEquals(url, "%s/%s" % (self.impl.request.url, "key"))
        self.mox.VerifyAll()        
        
class MockFeedHandler(FeedHandler, BaseAuthorizationHandler):
    def __init__(self, handler, svc):
        FeedHandler.__init__(self)
        self.handler = handler
        self.svc = svc

    def get_entries(self, parent, limit, offset):
        return self.handler.get_entries(parent, limit, offset)

    def create_param_map(self, user, all_entries, can_write, now):
        return {}
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_html(self, parent, entries, prev_link, next_link, msg):
        self.handler.render_html(parent, entries, prev_link, next_link, msg)

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

    def render_string(self, s):
        self.handler.render_string(s)

    def handle_post_success(self, parent_entry, new_entry):
        self.handler.handle_post_success(parent_entry, new_entry)

    def get_parent_name(self):
        return "parent"

    def get_entries_name(self):
        return "children"

    def get_svc(self):
        return self.svc

if __name__ == '__main__':
    unittest.main()

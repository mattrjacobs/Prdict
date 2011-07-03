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
from handlers.entry import EntryHandler 
from models.abstract_model import AbstractModel
from services.base_svc import BaseService
from utils.constants import Constants

class TestEntryHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'title' : 'New Entry',
                              'description' : 'New Entry Description',
                              'ref_id' : 'ref_id' }

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(EntryHandler)
        self.mock_svc = self.mox.CreateMock(BaseService)
        self.impl = MockEntryHandler(self.mock_handler, self.mock_svc)

    def JsonFromSport(self, sportJson):
        readJson = json.loads(sportJson)
        title_ok = self.sport.title == readJson['title']
        desc_ok = self.sport.description == readJson['description']
        link_ok = "/api/sports/%s" % self.sport.key() == readJson['link']
        leagues_ok = "/api/sports/%s/leagues" % self.sport.key() == \
                     readJson['leagues']
        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0

        return title_ok and desc_ok and link_ok and leagues_ok and \
               created_ok and updated_ok 

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.mock_handler.render_html(mox.Func(self.SameSportKey), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.sport_key)
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_html(mox.Func(self.SameSportKey), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.sport_key)
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_html(mox.Func(self.SameSportKey), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.sport_key)
        self.mox.VerifyAll()        

    def testGetJsonWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_string(mox.Func(self.JsonFromSport))
        self.mox.ReplayAll()

        self.impl.get(self.sport_key)
        self.mox.VerifyAll()

class MockEntryHandler(EntryHandler, BaseAuthorizationHandler):
    def __init__(self, handler, svc):
        EntryHandler.__init__(self)
        self.handler = handler
        self.svc = svc
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_html(self, entry, msg = None):
        self.handler.render_html(entry, msg)

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

    def render_string(self, s):
        self.handler.render_string(s)

    def get_svc(self):
        return self.svc
        
if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.user import UserHandler 
from models.prdict_user import PrdictUser
from utils.constants import Constants

class TestUserHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'email' : self.email,
                              'username' : self.username }

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(UserHandler)
        self.impl = MockUserHandler(self.mock_handler)

    def JsonFromUser(self, userJson):
        readJson = json.loads(userJson)
        email_ok = self.email == readJson['email']
        username_ok = self.username == readJson['username']
        link_ok = "/api/users/%s" % self.user.key() == readJson['link']
        friends_ok = "/api/users/%s/friends" % self.user.key() == \
                     readJson['friends']
        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0

        return email_ok and username_ok and link_ok and friends_ok and \
               created_ok and updated_ok 

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.user_key)
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("user.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.user_key)
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("user.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.user_key)
        self.mox.VerifyAll()        

    def testGetJsonWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_string(mox.Func(self.JsonFromUser))
        self.mox.ReplayAll()

        self.impl.get(self.user_key)
        self.mox.VerifyAll()

    def testFormPutNotAllowed(self):
        self.set_user(self.username, True)
        self.impl.request = \
                          self.req("email=diff_user@prdict.com&username=diffie", "PUT")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(405)
        self.mox.ReplayAll()

        self.impl.put(self.user_key)
        self.mox.VerifyAll()

    def testJsonPutNotAllowed(self):
        json_post = json.dumps({ 'email' : 'diff_user@prdict.com',
                                 'username' : 'diffie' })

        self.set_user(self.username, True)
        self.impl.request = self.req(json_post, "PUT")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.response.set_status(405)
        self.mox.ReplayAll()

        self.impl.put(self.user_key)
        self.mox.VerifyAll()

class MockUserHandler(UserHandler):
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

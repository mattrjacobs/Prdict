#!/usr/bin/env python

import logging
import mox
import unittest
import urllib

from google.appengine.api.users import User
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.users import UsersHandler 
from utils.constants import Constants

class TestUsersHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.email, False)

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(UsersHandler)
        self.impl = MockUsersHandler(self.mock_handler)

    def SameUserInDict(self, dict):
        return dict["user"].key() == self.user.key()

    #CLOSEDBETA : Eventually we want a 200 for anonymous users
    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    #CLOSEDBETA : Eventually we want a 200 for non-admin users
    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()        

    #CLOSEDBETA : Eventually we want a 201 for anonymous users
    def testPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidContentType(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = "invalid content type"
        self.impl.response.set_status(415)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamEmptyEmail(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : '',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamMissingEmail(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamTooLongEmail(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : "%s@toolong.com" % ['a' for x in range(1, 80)],
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamEmailNotValid(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamEmptyUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : '' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamMissingUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamTooShortUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'a' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamTooLongUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : ['a' for x in range(1, 21)] }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamUsernameAlreadyTaken(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : self.username }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamUsernameContainsWhitespace(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : "aaa bbb" }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostValidPostParamAlreadyExistsAsAdmin(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : self.email,
              'username' : 'some_new_username' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(302)
        self.mock_handler.render_template("user.html", mox.Func(self.SameUserInDict))
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedUser(url, self.email)
        self.mox.VerifyAll()

    def testPostValidPostParamGAEReadOnly(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_user") 

        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.create_user("new_user", mox.IsA(User)).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.render_template("503.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertFalse(self.impl.response.headers.has_key("Content-Location"))
        self.mox.VerifyAll()

    def testPostValidPostParamAsNonAdmin(self):
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostValidPostParamCreateNewUserAsAdmin(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(201)
        self.mock_handler.render_template("user.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedUser(url, "new_user@prdict.com")
        self.mox.VerifyAll()

    def verifyReturnedUser(self, url, expected_email):
        user_key = url[url.rindex("/") + 1:]
        returned_user = db.get(db.Key(encoded = user_key))
        self.assertEquals(returned_user.email, expected_email)
        
class MockUsersHandler(UsersHandler):
    def __init__(self, handler):
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

if __name__ == '__main__':
    unittest.main()

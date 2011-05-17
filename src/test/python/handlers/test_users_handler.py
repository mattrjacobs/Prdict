#!/usr/bin/env python

import logging
import mox
import simplejson as json
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
        self.new_username = "new_user"
        self.new_user_email = "new_user@prdict.com"
        self.new_user_key = None

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(UsersHandler)
        self.impl = MockUsersHandler(self.mock_handler)

    def SameUserInDict(self, dict):
        return str(dict['user'].key()) == self.user_key

    def SameJsonUser(self, json_user):
        readJson = json.loads(json_user)
        return readJson['email'] == self.email and \
               readJson['username'] == self.user.username and \
               readJson['link'] == "/api/users/%s" % self.user.key() and \
               readJson['friends'] == \
               "/api/users/%s/friends" % self.user.key() and \
               len(readJson['created']) > 0 and \
               len(readJson['updated']) > 0

    def NewUserJsonPost(self, json_user):
        readJson = json.loads(json_user)
        return readJson['email'] == self.new_user_email and \
               readJson['username'] == self.new_username and \
               len(readJson['created']) > 0 and \
               len(readJson['updated']) > 0
    
    #CLOSEDBETA : Eventually we want a 200 for anonymous users
    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    #CLOSEDBETA : Eventually we want a 200 for non-admin users
    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
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
    def testFormPostWithNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    #CLOSEDBETA : Eventually we want a 201 for anonymous users
    def testJsonPostWithNoUser(self):
        json_post = json.dumps({ 'email' : 'new_user@prdict.com',
                                 'username' : 'new_user' })

        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(403)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
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

    def testFormPostInvalidPostParamEmptyEmail(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : '',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamEmptyEmail(self):
        json_post = json.dumps({ 'email' : '',
                                 'username' : 'new_user' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamMissingEmail(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamMissingEmail(self):
        json_post = json.dumps({ 'username' : 'new_user' })
        
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamTooLongEmail(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : "%s@toolong.com" % ['a' for x in range(1, 80)],
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamTooLongEmail(self):
        json_post = json.dumps({' email' : "%s@toolong.com" % \
                                ['a' for x in range(1, 80)],
                                'username' : 'new_user' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamEmailNotValid(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonFormPostInvalidPostParamEmailNotValid(self):
        json_post = json.dumps({ 'email' : 'new_user',
                                 'username' : 'new_user' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamEmptyUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : '' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamEmptyUsername(self):
        json_post = json.dumps({ 'email' : 'new_user@prdict.com',
                                 'username' : '' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamMissingUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamMissingUsername(self):
        json_post = json.dumps({ 'email' : 'new_user@prdict.com' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamTooShortUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'a' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamTooShortUsername(self):
        json_post = json.dumps({ 'email' : 'new_user@prdict.com',
                                 'username' : 'a' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamTooLongUsername(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : ''.join(['a' for x in range(1, 22)]) }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamTooLongUsername(self):
        json_post = json.dumps({ 'email' : 'new_user@prdict.com',
                                 'username' : ''.join(['a' for x in range(1,22)]) })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testPostInvalidPostParamUsernameAlreadyTaken(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : self.username }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostInvalidPostParamUsernameContainsWhitespace(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : "aaa bbb" }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_template("users.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostInvalidPostParamUsernameContainsWhitespace(self):
        json_post = json.dumps({ 'email' : 'new_user@prdict.com',
                                 'username' : 'aaa bbb' })

        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request = self.req(json_post, "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(400)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostValidPostParamAlreadyExistsAsAdmin(self):
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

    def testJsonPostValidPostParamAlreadyExistsAsAdmin(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(json.dumps(
            { 'email' : self.email,
              'username' : 'some_new_username' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.response.set_status(302)
        self.mock_handler.render_string(mox.Func(self.SameJsonUser))
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedUser(url, self.email)
        self.mox.VerifyAll()

    def testFormPostValidPostParamGAEReadOnly(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
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

    def testJsonPostValidPostParamGAEReadOnly(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_user") 

        self.impl.request = self.req(json.dumps(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.create_user("new_user", mox.IsA(User)).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.assertFalse(self.impl.response.headers.has_key("Content-Location"))
        self.mox.VerifyAll()

    def testFormPostValidPostParamAsNonAdmin(self):
        self.impl.request = self.req(urllib.urlencode(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testJsonPostValidPostParamAsNonAdmin(self):
        self.impl.request = self.req(json.dumps(
            { 'email' : 'new_user@prdict.com',
              'username' : 'new_user' }), "POST")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.response.set_status(403)
        self.mock_handler.render_string(mox.Func(self.JsonPostResponseError))
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostValidPostParamCreateNewUserAsAdmin(self):
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

    def testJsonPostValidPostParamCreateNewUserAsAdmin(self):
        self.set_user(self.email, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(json.dumps(
            { 'email' : self.new_user_email,
              'username' : self.new_username }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        
        self.impl.response.set_status(201)
        self.mock_handler.render_string(mox.Func(self.NewUserJsonPost))
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

    def render_string(self, s):
        self.handler.render_string(s)

if __name__ == '__main__':
    unittest.main()

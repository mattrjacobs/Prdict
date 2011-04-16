#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.sports import SportsHandler 
from models.sport import Sport
from utils.constants import Constants

class TestSportsHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.valid_params = { 'title' : 'New Sport',
                              'description' : 'New Sport Description'}

        self.sport_2 = self._create_sport("Sport 2", "")
        self.sport_3 = self._create_sport("Sport 3", "")

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(SportsHandler)
        self.impl = MockSportsHandler(self.mock_handler)

    def JsonFromSports(self, sportsJson):
        readJson = json.loads(sportsJson)
        sport_1 = filter(lambda sport: sport['title'] == "Sport 1", readJson)[0]
        sport_2 = filter(lambda sport: sport['title'] == "Sport 2", readJson)[0]
        sport_3 = filter(lambda sport: sport['title'] == "Sport 3", readJson)[0]
        sport_1_ok = sport_1['description'] == '' and \
                     sport_1['link'] == \
                     "/api/sports/%s" % self.sport.key() and \
                     sport_1['leagues'] == \
                     "/api/sports/%s/leagues" % self.sport.key() and \
                     len(sport_1['created']) > 0 and \
                     len(sport_1['updated']) > 0
        sport_2_ok = sport_2['description'] == '' and \
                     sport_2['link'] == \
                     "/api/sports/%s" % self.sport_2.key() and \
                     sport_2['leagues'] == \
                     "/api/sports/%s/leagues" % self.sport_2.key() and \
                     len(sport_2['created']) > 0 and \
                     len(sport_2['updated']) > 0
        sport_3_ok = sport_3['description'] == '' and \
                     sport_3['link'] == \
                     "/api/sports/%s" % self.sport_3.key() and \
                     sport_3['leagues'] == \
                     "/api/sports/%s/leagues" % self.sport_3.key() and \
                     len(sport_3['created']) > 0 and \
                     len(sport_3['updated']) > 0
        return sport_1_ok and sport_2_ok and sport_3_ok

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().AndReturn(None)
        self.mock_handler.render_template("sports.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("sports.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("sports.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get()
        self.mox.VerifyAll()        

    def testJsonGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.render_string(mox.Func(self.JsonFromSports))
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
        self.mock_handler.render_template("sports.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.mox.VerifyAll()

    def testFormPostMissingTitle(self):
        invalid_params = { 'description' : 'New Sport Description'}

        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("sports.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()

    def testJsonPostMissingTitle(self):
        invalid_params = { 'description' : 'New Sport Description'}

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
                           'description' : 'New Sport Description'}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.impl.response.set_status(400)
        self.mock_handler.render_template("sports.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        self.impl.post()

        self.mox.VerifyAll()
        
    def testJsonPostEmptyTitle(self):
        invalid_params = { 'title' : '',
                           'description' : 'New Sport Description'}
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
        invalid_params = { 'title' : 'New Sport'}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_template("sport.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedSport(url, {'title' : 'New Sport', 'description' : ''})
        self.mox.VerifyAll()

    def testJsonPostMissingDesc(self):
        invalid_params = { 'title' : 'New Sport'}
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
        self.verifyReturnedSport(url, {'title' : 'New Sport', 'description' : ''})
        self.mox.VerifyAll()

    def testFormPostEmptyDesc(self):
        invalid_params = { 'title' : 'New Sport',
                           'description' : ''}
        self.set_user(self.username, True)
        self.impl.request = self.req(urllib.urlencode(invalid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.response.set_status(201)
        self.mock_handler.render_template("sport.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedSport(url, {'title' : 'New Sport', 'description' : ''})
        self.mox.VerifyAll()

    def testJsonPostEmptyDesc(self):
        invalid_params = { 'title' : 'New Sport',
                           'description' : ''}
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
        self.verifyReturnedSport(url, {'title' : 'New Sport', 'description' : ''})
        self.mox.VerifyAll()

    def testFormPostValidPostParamGAEReadOnly(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mox.StubOutWithMock(self.impl, "create_item") 

        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.create_item(("New Sport", "New Sport Description")).AndRaise(CapabilityDisabledError)
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
        
        self.impl.create_item(("New Sport", "New Sport Description")).AndRaise(CapabilityDisabledError)
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

    def testFormPostValidPostParamAsAdminCreateNewSport(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.impl.request = self.req(urllib.urlencode(self.valid_params), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        
        self.impl.response.set_status(201)
        self.mock_handler.render_template("sport.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.post()
        self.assertTrue(len(self.impl.response.headers["Content-Location"]) > 0)
        url = self.impl.response.headers["Content-Location"]
        self.verifyReturnedSport(url, self.valid_params)
        self.mox.VerifyAll()

    def testJsonPostValidPostParamAsAdminCreateNewSport(self):
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
        self.verifyReturnedSport(url, self.valid_params)
        self.mox.VerifyAll()

    def verifyReturnedSport(self, url, expected_params):
        sport_key = url[url.rindex("/") + 1:]
        returned_sport = db.get(db.Key(encoded = sport_key))
        self.assertEquals(returned_sport.title, expected_params['title'])
        self.assertEquals(returned_sport.description, expected_params['description'])
        
class MockSportsHandler(SportsHandler):
    def __init__(self, handler):
        SportsHandler.__init__(self)
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

    def render_string(self, s):
        self.handler.render_string(s)

if __name__ == '__main__':
    unittest.main()

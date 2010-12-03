#!/usr/bin/env python

from datetime import datetime
import logging
import mox
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.event import EventHandler 
from models.event import Event
from utils.constants import Constants

class TestEventHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.start_date = '2012-01-01 01:00:00'
        self.end_date = '2012-01-01 04:00:00'

        self.valid_params = { 'title' : 'New Event',
                              'description' : 'New Event Description',
                              'start_date' : self.start_date,
                              'end_date' : self.end_date}

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(EventHandler)
        self.impl = MockEventHandler(self.mock_handler)

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.mock_handler.render_template("event.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("event.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("event.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()        

class MockEventHandler(EventHandler):
    def __init__(self, handler):
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)

if __name__ == '__main__':
    unittest.main()

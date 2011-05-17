#!/usr/bin/env python

from datetime import datetime
import logging
import mox
import simplejson as json
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

    def JsonFromEvent(self, eventJson):
        readJson = json.loads(eventJson)
        title_ok = self.event.title == readJson['title']
        desc_ok = self.event.description == readJson['description']
        link_ok = "/api/events/%s" % self.event.key() == readJson['link']
        start_date_ok = self.event.start_date_str == readJson['start_date']
        end_date_ok = self.event.end_date_str == readJson['end_date']
        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0
        return title_ok and desc_ok and link_ok and start_date_ok and \
               end_date_ok and created_ok and updated_ok

    def JsonFromSportsEvent(self, eventJson):
        readJson = json.loads(eventJson)
        title_ok = self.sports_event.title == readJson['title']
        desc_ok = self.sports_event.description == readJson['description']
        home_team_ok = self.team_1.title == \
                       readJson['home_team']['title'] and \
                       self.team_1.location == \
                       readJson['home_team']['location'] and \
                       "/api/teams/%s" % str(self.team_1.key()) == \
                       readJson['home_team']['link']
        away_team_ok = self.team_2.title == \
                       readJson['away_team']['title'] and \
                       self.team_2.location == \
                       readJson['away_team']['location'] and \
                       "/api/teams/%s" % str(self.team_2.key()) == \
                       readJson['away_team']['link']
        league_ok = self.league.title == readJson['league']['title'] and \
                    "/api/leagues?%s" % str(self.league.key()) == \
                    readJson['league']['link']
        completed_ok = self.sports_event.completed == readJson['completed']
        home_team_score_ok = self.sports_event.home_team_score == \
                             readJson['home_team_score']
        away_team_score_ok = self.sports_event.away_team_score == \
                             readJson['away_team_score']
        game_kind_ok = self.sports_event.game_kind == readJson['game_kind']
        link_ok = "/api/events/%s" % self.sports_event.key() == readJson['link']
        start_date_ok = self.sports_event.start_date_str == readJson['start_date']
        end_date_ok = self.sports_event.end_date_str == readJson['end_date']
        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0
        return title_ok and desc_ok and home_team_ok and away_team_ok and \
               completed_ok and home_team_score_ok and \
               away_team_score_ok and game_kind_ok and link_ok and \
               start_date_ok and  end_date_ok and created_ok and updated_ok

    def testGetEventNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.mock_handler.render_template("event.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetEventWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("event.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetEventWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_template("event.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()        

    def testGetEventJsonWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_string(mox.Func(self.JsonFromEvent))
        self.mox.ReplayAll()
        
        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetSportsEventJsonWithAdminUser(self):
        self.set_user(self.username, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_string(mox.Func(self.JsonFromSportsEvent))
        self.mox.ReplayAll()
        
        self.impl.get(self.sports_event_key)
        self.mox.VerifyAll()
        
class MockEventHandler(EventHandler):
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

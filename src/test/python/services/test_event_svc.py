#!/usr/bin/env python

import logging
import simplejson as json
import unittest
import urllib

from base_service_test import BaseServiceTest
from services.event_svc import EventService

class TestEventService(BaseServiceTest):
    def setUp(self):
        BaseServiceTest.setUp(self)
        self.title = "New Event"
        self.desc = "New Event Description"
        self.start_date_str = "2011-05-17 00:18:15"
        self.end_date_str = "2011-05-17 03:18:15"
        self.home_team_score_str = "91"
        self.away_team_score_str = "70"
        self.completed_str = "false"
        self.ref_id = "ref_id"
        self.game_kind = "Regular Season"
        self.impl = EventService()

    def tearDown(self):
        BaseServiceTest.tearDown(self)

    def testPostEmptyJson(self):
        req = self.req("", "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 0)

    def testPostEmptyForm(self):
        req = self.req("", "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 0)

    def testPostJsonEvent(self):
        req = self.req(json.dumps({ "title" : self.title,
                                    "description" : self.desc,
                                    "start_date" : self.start_date_str,
                                    "end_date" : self.end_date_str,
                                    "type" : "event" }),
                       "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 5)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(params["start_date_str"], self.start_date_str)
        self.assertEquals(params["end_date_str"], self.end_date_str)
        self.assertEquals(params["type"], "event")

    def testPostFormEvent(self):
        req = self.req(urllib.urlencode({ "title" : self.title,
                                          "description" : self.desc,
                                          "start_date" : self.start_date_str,
                                          "end_date" : self.end_date_str,
                                          "type" : "event" }),
                       "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 5)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(params["start_date_str"], self.start_date_str)
        self.assertEquals(params["end_date_str"], self.end_date_str)
        self.assertEquals(params["type"], "event")

    def testPostJsonUnknownType(self):
        req = self.req(json.dumps({ "title" : self.title,
                                    "description" : self.desc,
                                    "start_date" : self.start_date_str,
                                    "end_date" : self.end_date_str,
                                    "type" : "not-an-event" }),
                       "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 0)

    def testPostFormUnknownType(self):
        req = self.req(urllib.urlencode({ "title" : self.title,
                                          "description" : self.desc,
                                          "start_date" : self.start_date_str,
                                          "end_date" : self.end_date_str,
                                          "type" : "not-an-event" }),
                       "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 0)

    def testPostJsonSportsEvent(self):
        req = self.req(json.dumps({ "title" : self.title,
                                    "description" : self.desc,
                                    "start_date" : self.start_date_str,
                                    "end_date" : self.end_date_str,
                                    "type" : "sportsevent",
                                    "home_team" : self.team_1.relative_url,
                                    "away_team" : self.team_2.relative_url,
                                    "league" : self.league.relative_url,
                                    "completed" : self.completed_str,
                                    "home_team_score" : self.home_team_score_str,
                                    "away_team_score" : self.away_team_score_str,
                                    'ref_id' : self.ref_id,
                                    "game_kind" : self.game_kind }),
                       "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 13)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(params["start_date_str"], self.start_date_str)
        self.assertEquals(params["end_date_str"], self.end_date_str)
        self.assertEquals(params["type"], "sportsevent")
        self.assertEquals(params["home_team_str"], self.team_1.relative_url)
        self.assertEquals(params["away_team_str"], self.team_2.relative_url)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["completed_str"], self.completed_str)
        self.assertEquals(params["home_team_score_str"], self.home_team_score_str)
        self.assertEquals(params["away_team_score_str"], self.away_team_score_str)
        self.assertEquals(params["ref_id"], self.ref_id)
        self.assertEquals(params["game_kind"], self.game_kind)

    def testPostFormSportsEvent(self):
        req = self.req(urllib.urlencode({ "title" : self.title,
                                          "description" : self.desc,
                                          "start_date" : self.start_date_str,
                                          "end_date" : self.end_date_str,
                                          "type" : "sportsevent",
                                          "home_team" : self.team_1.relative_url,
                                          "away_team" : self.team_2.relative_url,
                                          "league" : self.league.relative_url,
                                          "completed" : self.completed_str,
                                          "home_team_score" : self.home_team_score_str,
                                          "away_team_score" : self.away_team_score_str,
                                          "ref_id" : self.ref_id,
                                          "game_kind" : self.game_kind }),
                       "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 13)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(params["start_date_str"], self.start_date_str)
        self.assertEquals(params["end_date_str"], self.end_date_str)
        self.assertEquals(params["type"], "sportsevent")
        self.assertEquals(params["home_team_str"], self.team_1.relative_url)
        self.assertEquals(params["away_team_str"], self.team_2.relative_url)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["completed_str"], self.completed_str)
        self.assertEquals(params["home_team_score_str"], self.home_team_score_str)
        self.assertEquals(params["away_team_score_str"], self.away_team_score_str)
        self.assertEquals(params["ref_id"], self.ref_id)
        self.assertEquals(params["game_kind"], self.game_kind)
        

if __name__ == '__main__':
    unittest.main()

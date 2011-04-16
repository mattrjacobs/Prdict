#!/usr/bin/env python

import logging
import simplejson as json
import unittest
import urllib

from base_service_test import BaseServiceTest
from services.league_svc import LeagueService

class TestLeagueService(BaseServiceTest):
    def setUp(self):
        BaseServiceTest.setUp(self)
        self.title = "New League"
        self.desc = "New League Description"
        self.valid_params = { 'title' : self.title,
                              'description' : self.desc,
                              'sport' : self.sport.title }
        self.impl = LeagueService()

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

    def testPostJsonMissingTitle(self):
        req = self.req(json.dumps({ "description" : self.desc,
                                    "sport" : self.sport.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostFormMissingTitle(self):
        req = self.req(urllib.urlencode({ "description" : self.desc,
                                          "sport" : self.sport.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostJsonEmptyTitle(self):
        req = self.req(json.dumps({ "title": "",
                                    "description" : self.desc,
                                    "sport" : self.sport.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostFormEmptyTitle(self):
        req = self.req(urllib.urlencode({ "title": "",
                                          "description" : self.desc,
                                          "sport" : self.sport.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)
        
    def testPostJsonMissingDesc(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "sport" : self.sport.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostFormMissingDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "sport" : self.sport.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(str(params["sport"].key()), self.sport_key)
        
    def testPostJsonEmptyDesc(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : "",
                                    "sport" : self.sport.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostFormEmptyDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : "",
                                          "sport" : self.sport.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')
        self.assertEquals(str(params["sport"].key()), self.sport_key)
        
    def testPostJsonMissingSport(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc, }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostFormMissingSport(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc, }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostJsonEmptySport(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "sport" : '' }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostFormEmptySport(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "sport" : '' }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostJsonInvalidSport(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "sport" : "not-a-sport" }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testFormJsonInvalidSport(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "sport" : "not-a-sport" }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostJsonSportFromBodyAndUrlDoNotMatch(self):
        req = self.reqWithPath(json.dumps({ "title": self.title,
                                            "description" : self.desc,
                                            "sport" : self.sport.title }),
                               "POST",
                               "/api/sports/not-a-sport/leagues")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostFormSportFromBodyAndUrlDoNotMatch(self):
        req = self.reqWithPath(urllib.urlencode({ "title": self.title,
                                                  "description" : self.desc,
                                                  "sport" : self.sport.title }),
                               "POST",
                               "/api/sports/not-a-sport/leagues")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostFormValidSportFromUrl(self):
        req = self.reqWithPath(urllib.urlencode({ "title": self.title,
                                                  "description" : self.desc }),
                               "POST",
                               "/api/sports/%s/leagues" % self.sport.key())
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)
        
    def testPostJsonValidSportFromBody(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "sport" : self.sport.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostFormValidSportFromBody(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "sport" : self.sport.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostJsonValidSportFromUrlAndBody(self):
        req = self.reqWithPath(json.dumps({ "title": self.title,
                                            "description" : self.desc,
                                            "sport" : self.sport.title }),
                               "POST",
                               "/api/sports/%s/leagues" % self.sport.key())
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

    def testPostFormValidSportFromUrlAndBody(self):
        req = self.reqWithPath(urllib.urlencode({ "title": self.title,
                                                  "description" : self.desc,
                                                  "sport" : self.sport.title }),
                               "POST",
                               "/api/sports/%s/leagues" % self.sport.key())
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["sport"].key()), self.sport_key)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

import logging
import simplejson as json
import unittest
import urllib

from base_service_test import BaseServiceTest
from services.team_svc import TeamService

class TestTeamService(BaseServiceTest):
    def setUp(self):
        BaseServiceTest.setUp(self)
        self.title = "New Team"
        self.desc = "New Team Description"
        self.ref_id = "ref_id"
        self.impl = TeamService()

    def tearDown(self):
        BaseServiceTest.tearDown(self)

    def testPostJsonMissingTitle(self):
        req = self.req(json.dumps({ "description" : self.desc,
                                    "league" : self.league.relative_url }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)

    def testPostFormMissingTitle(self):
        req = self.req(urllib.urlencode({ "description" : self.desc,
                                          "league" : self.league.relative_url }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)

    def testPostJsonEmptyTitle(self):
        req = self.req(json.dumps({ "title": "",
                                    "description" : self.desc,
                                    "league" : self.league.relative_url }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)

    def testPostFormEmptyTitle(self):
        req = self.req(urllib.urlencode({ "title": "",
                                          "description" : self.desc,
                                          "league" : self.league.relative_url }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)
        
    def testPostJsonMissingDesc(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "league" : self.league.relative_url }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(str(params["league"].key()), self.league_key)

    def testPostFormMissingDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "league" : self.league.relative_url }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(str(params["league"].key()), self.league_key)
        
    def testPostJsonEmptyDesc(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : "",
                                    "league" : self.league.relative_url }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')
        self.assertEquals(str(params["league"].key()), self.league_key)

    def testPostFormEmptyDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : "",
                                          "league" : self.league.relative_url }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')
        self.assertEquals(str(params["league"].key()), self.league_key)
        
    def testPostJsonMissingLeague(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc, }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostFormMissingLeague(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc, }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostJsonEmptyLeague(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "league" : '' }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostFormEmptyLeague(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "league" : '' }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostJsonInvalidLeague(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "league" : "not-a-league" }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testFormJsonInvalidLeague(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "league" : "not-a-league" }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostJsonLeagueFromBodyAndUrlDoNotMatch(self):
        req = self.reqWithPath(json.dumps({ "title": self.title,
                                            "description" : self.desc,
                                            "league" : self.league.relative_url }),
                               "POST",
                               "/api/leagues/not-a-league/teams")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

    def testPostFormLeagueFromBodyAndUrlDoNotMatch(self):
        req = self.reqWithPath(urllib.urlencode({ "title": self.title,
                                                  "description" : self.desc,
                                                  "league" : self.league.relative_url }),
                               "POST",
                               "/api/leagues/not-a-league/teams")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostFormValidLeagueFromUrl(self):
        req = self.reqWithPath(urllib.urlencode({ "title": self.title,
                                                  "description" : self.desc,
                                                  "ref_id" : self.ref_id }),
                               "POST",
                               "/api/leagues/%s/teams" % self.league.key())
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 4)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["ref_id"], self.ref_id)
        
    def testPostJsonValidLeagueFromBody(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "league" : self.league.relative_url,
                                    "ref_id": self.ref_id }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 4)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["ref_id"], self.ref_id)

    def testPostFormValidLeagueFromBody(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "league" : self.league.relative_url,
                                          "ref_id": self.ref_id }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 4)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["ref_id"], self.ref_id)

    def testPostJsonValidLeagueFromUrlAndBody(self):
        req = self.reqWithPath(json.dumps({ "title": self.title,
                                            "description" : self.desc,
                                            "league" : self.league.relative_url,
                                            "ref_id" : self.ref_id }),
                               "POST",
                               "/api/leagues/%s/teams" % self.league.key())
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 4)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["ref_id"], self.ref_id)

    def testPostFormValidLeagueFromUrlAndBody(self):
        req = self.reqWithPath(urllib.urlencode({ "title": self.title,
                                                  "description" : self.desc,
                                                  "league" : self.league.relative_url,
                                                  "ref_id" : self.ref_id }),
                               "POST",
                               "/api/leagues/%s/teams" % self.league.key())
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 4)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(str(params["league"].key()), self.league_key)
        self.assertEquals(params["ref_id"], self.ref_id)

if __name__ == '__main__':
    unittest.main()

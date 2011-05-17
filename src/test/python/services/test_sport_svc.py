#!/usr/bin/env python

import logging
import simplejson as json
import unittest
import urllib

from base_service_test import BaseServiceTest
from services.sport_svc import SportService

class TestSportService(BaseServiceTest):
    def setUp(self):
        BaseServiceTest.setUp(self)
        self.title = "New Sport"
        self.desc = "New Sport Description"
        self.impl = SportService()

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
        req = self.req(json.dumps({ "description" : self.desc }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 1)
        self.assertEquals(params["description"], self.desc)

    def testPostFormMissingTitle(self):
        req = self.req(urllib.urlencode({ "description" : self.desc }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 1)
        self.assertEquals(params["description"], self.desc)

    def testPostJsonEmptyTitle(self):
        req = self.req(json.dumps({ "title": "",
                                    "description" : self.desc }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)

    def testPostFormEmptyTitle(self):
        req = self.req(urllib.urlencode({ "title": "",
                                          "description" : self.desc }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)
         
    def testPostJsonMissingDesc(self):
        req = self.req(json.dumps({ "title": self.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 1)
        self.assertEquals(params["title"], self.title)

    def testPostFormMissingDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 1)
        self.assertEquals(params["title"], self.title)
        
    def testPostJsonEmptyDesc(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : "" }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')

    def testPostFormEmptyDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : "" }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')
        
    def testPostFormValid(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc }),"POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        
    def testPostJsonValid(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 2)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)

if __name__ == '__main__':
    unittest.main()

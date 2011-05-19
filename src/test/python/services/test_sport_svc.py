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
        self.ref_id = "ref_id"
        self.impl = SportService()

    def tearDown(self):
        BaseServiceTest.tearDown(self)

    def testPostJsonMissingTitle(self):
        req = self.req(json.dumps({ "description" : self.desc }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["description"], self.desc)

    def testPostFormMissingTitle(self):
        req = self.req(urllib.urlencode({ "description" : self.desc }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["description"], self.desc)

    def testPostJsonEmptyTitle(self):
        req = self.req(json.dumps({ "title": "",
                                    "description" : self.desc }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)

    def testPostFormEmptyTitle(self):
        req = self.req(urllib.urlencode({ "title": "",
                                          "description" : self.desc }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], "")
        self.assertEquals(params["description"], self.desc)
         
    def testPostJsonMissingDesc(self):
        req = self.req(json.dumps({ "title": self.title }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)

    def testPostFormMissingDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        
    def testPostJsonEmptyDesc(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : "" }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')

    def testPostFormEmptyDesc(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : "" }), "POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], '')
        
    def testPostFormValid(self):
        req = self.req(urllib.urlencode({ "title": self.title,
                                          "description" : self.desc,
                                          "ref_id" : self.ref_id }),"POST")
        params = self.impl.get_form_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(params["ref_id"], self.ref_id)
        
    def testPostJsonValid(self):
        req = self.req(json.dumps({ "title": self.title,
                                    "description" : self.desc,
                                    "ref_id" : self.ref_id }), "POST")
        params = self.impl.get_json_params(req)

        self.assertEquals(len(params), 3)
        self.assertEquals(params["title"], self.title)
        self.assertEquals(params["description"], self.desc)
        self.assertEquals(params["ref_id"], self.ref_id)

if __name__ == '__main__':
    unittest.main()

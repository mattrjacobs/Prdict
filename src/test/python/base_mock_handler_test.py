#!/usr/bin/env python
from cStringIO import StringIO
from datetime import datetime
import mox
import os
import unittest
import wsgiref

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import user_service_stub
from google.appengine.api import users
from google.appengine.ext.webapp import Request
from google.appengine.ext.webapp import Response 

from models.event import Event
from models.prdict_user import PrdictUser

APP_ID = 'Prdict API'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@prdict.com'
SERVER_NAME = 'localhost'
SERVER_PORT = '8080'
URL_SCHEME = 'http'

DATASTORE_STUB_NAME = 'datastore_v3'
USER_SERVICE_STUB_NAME = 'user'

class BaseMockHandlerTest(unittest.TestCase):
    def setUp(self):
        os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
        os.environ['APPLICATION_ID'] = APP_ID
        os.environ['SERVER_NAME'] = SERVER_NAME
        os.environ['SERVER_PORT'] = SERVER_PORT
        os.environ['wsgi.url_scheme'] = URL_SCHEME
        os.environ['USER_IS_ADMIN'] = "0"

        self.mox = mox.Mox()
        
        self.stub_req = self.req("", "GET")
        self.mock_resp = self.mox.CreateMock(Response)
        self.mock_resp.headers = wsgiref.headers.Headers([])

        self.original_apiproxy = apiproxy_stub_map.apiproxy
        self.clear_datastore()
        self.clear_userstore()

        self.define_impl()

        self.impl.request = self.stub_req
        self.impl.response = self.mock_resp

        self.username = LOGGED_IN_USER

        self.user = self._create_user("Prdict User", self.username)

        self.friend_username = "friend@prdict.com"
        self.friend_user = self._create_user('Prdict Friend', self.friend_username)
        self.non_friend_username = "non_friend@prdict.com"
        self.non_friend_user = self._create_user('Non-Friend User', self.non_friend_username)
        self.event = self._create_event("Event 1", "Event 1 Desc", "2012-1-1 08:00:00", "2012-1-1 11:00:00")

    def tearDown(self):
        apiproxy_stub_map.apiproxy = self.original_apiproxy

    def define_impl(self):
        raise "Not implemented"

    def clear_datastore(self):
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        stub = datastore_file_stub.DatastoreFileStub(APP_ID, None,  None)
        apiproxy_stub_map.apiproxy.RegisterStub(DATASTORE_STUB_NAME, stub)

    def clear_userstore(self):
        apiproxy_stub_map.apiproxy.RegisterStub(USER_SERVICE_STUB_NAME, user_service_stub.UserServiceStub())

    def req(self, body, method):
        req = Request({'wsgi.url_scheme' : URL_SCHEME,
                       'wsgi.input' : StringIO(body),
                       'SERVER_NAME' : SERVER_NAME,
                       'SERVER_PORT' : SERVER_PORT})
        req.body = body
        req.method = method
        return req

    def set_user(self, username, is_admin):
        os.environ["USER_EMAIL"] = username
        if is_admin:
            os.environ["USER_IS_ADMIN"] = "1"
        else:
            os.environ["USER_IS_ADMIN"] = "0"

    def remove_user(self):
        del os.environ["USER_EMAIL"]

    def _create_user(self, name, email):
        user = PrdictUser(name = name, user = users.User(email))
        user_key = str(user.put())
        return user

    def _create_event(self, title, description, start_date_str, end_date_str):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        event = Event(title = title, description = description,
                      start_date = start_date, end_date = end_date)
        event_key = str(event.put())
        return event

    def expect_auth(self, value):
        self.mock_auth_handler.is_user_authorized_for_entry(mox.Func(self.SameUserKey),
                                                            mox.Func(self.SameEntryKey)).AndReturn(value)

    def SameEntryKey(self, entry):
        return entry.key() == self.entry.key()
        
    def SameUserKey(self, user):
        return user.key() == self.user.key()

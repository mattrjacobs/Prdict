#!/usr/bin/env python

import logging
import mox
import unittest
import urllib

from google.appengine.api.users import User
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.userfriend import UserSpecificFriendHandler 
from utils.constants import Constants

class TestUserSpecificFriendHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.email, False)
        self.user_key = str(self.user.key())
        self.friend_key = str(self.friend_user.key())
        self.non_friend_key = str(self.non_friend_user.key())

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(UserSpecificFriendHandler)
        self.impl = MockUserSpecificFriendHandler(self.mock_handler)

    def SameFriendKey(self, friend):
        return str(friend.key()) == self.friend_key

    def checkFriends(self, actual_list, expected_list):
        key_map = map(lambda user: user.key(), actual_list)
        #Would be nice to implement this as a fold
        in_key_map = map(lambda user: user.key() in key_map, expected_list)
        for val in in_key_map:
            if not val:
                return False
        return True

    def testGetNoUser(self):
        self.remove_user()
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html")
        self.mox.ReplayAll()
        
        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetInvalidUserKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("404.html")
        self.mox.ReplayAll()

        self.impl.get("abc", self.friend_key)
        self.mox.VerifyAll()

    def testGetInvalidFriendKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("404.html")
        self.mox.ReplayAll()

        self.impl.get(self.user_key, "abc")
        self.mox.VerifyAll()

    def testGetByNonFriend(self):
        self.set_user(self.non_friend_email, False)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html")
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetByUserSucceeds(self):
        self.mock_handler.render_html(mox.Func(self.SameFriendKey))
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetByFriendSucceeds(self):
        self.set_user(self.friend_email, False)
        self.mock_handler.render_html(mox.Func(self.SameFriendKey))
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetByAdminSucceeds(self):
        self.set_user(self.admin_email, True)
        self.mock_handler.render_html(mox.Func(self.SameFriendKey))
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetNonFriend404(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("404.html")
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.non_friend_key)
        self.mox.VerifyAll()

class MockUserSpecificFriendHandler(UserSpecificFriendHandler):
    def __init__(self, handler):
        self.handler = handler

    def render_html(self, friend):
        self.handler.render_html(friend)

    def render_template(self, template):
        self.handler.render_template(template)

if __name__ == '__main__':
    unittest.main()

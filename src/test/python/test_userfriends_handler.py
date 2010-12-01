#!/usr/bin/env python

import logging
import mox
import unittest
import urllib

from google.appengine.api.users import User
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.userfriends import UserFriendsHandler 
from utils.constants import Constants

class TestUserFriendsHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)

        self.user_2_username = "user_2@prdict.com"
        self.user_2 = self._create_user("Prdict User 2", self.user_2_username, [User(self.username), User(self.friend_username)])

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(UserFriendsHandler)
        self.impl = MockUserFriendsHandler(self.mock_handler)

    def FriendsListWithNewMember(self, friends):
        return self.checkFriends(friends, [self.friend_user, self.non_friend_user])

    def FriendsListWithOldMembersOnly(self, friends):
        return self.checkFriends(friends, [self.friend_user])

    def checkFriends(self, actual_list, expected_list):
        key_map = map(lambda user: user.key(), actual_list)
        #Would be nice to implement this as a fold
        in_key_map = map(lambda user: user.key() in key_map, expected_list)
        for val in in_key_map:
            if not val:
                return False
        return True

    def testGetEntriesNoUser(self):
        entries = self.impl.get_entries(None)
        self.assertEquals(len(entries), 0) 

    def testGetEntriesUserWithOneFriend(self):
        entries = self.impl.get_entries(self.user)
        self.assertEquals(len(entries), 1)
        key_map = map(lambda friend: friend.key(), entries)
        self.assertTrue(self.friend_user.key() in key_map)

    def testGetEntriesUserWithTwoFriends(self):
        entries = self.impl.get_entries(self.user_2)
        self.assertEquals(len(entries), 2)
        key_map = map(lambda friend: friend.key(), entries)
        self.assertTrue(self.user.key() in key_map)
        self.assertTrue(self.friend_user.key() in key_map)

    def testIsPostDataValidFalse(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : ''}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid()
        self.assertFalse(is_valid)

    def testIsPostDataValidUnregistered(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : 'unregistered_user@random.com'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid()
        self.assertFalse(is_valid)

    def testIsPostDataValidMyself(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.username}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid()
        self.assertFalse(is_valid)

    def testIsPostDataValidRegistered(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.friend_username}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid()
        self.assertTrue(is_valid)

    def testHandlePostUserNotAFriendYet(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.non_friend_username}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(201)
        self.mock_handler.render_html(self.user, mox.Func(self.FriendsListWithNewMember), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.user)
        self.assertEquals(len(self.user.friends), 2)
        self.assertTrue(self.non_friend_user.user in map(lambda user: user, self.user.friends))
        self.mox.VerifyAll()

    def testHandlePostGAEReadOnlyErrorPropagatesUp(self):
        self.mox.StubOutWithMock(self.impl, "add_to_friends")
        
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.non_friend_username}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.add_to_friends(self.user, mox.IsA(User)).AndRaise(CapabilityDisabledError)
        self.mox.ReplayAll()

        exceptionRaised = False
        try:
            self.impl.handle_post(self.user)
        except CapabilityDisabledError:
            exceptionRaised = True
        self.assertTrue(exceptionRaised)
        self.mox.VerifyAll()

    def testHandlePostUserAlreadyFriend(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.friend_username}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(302)
        self.mock_handler.render_html(self.user, mox.Func(self.FriendsListWithOldMembersOnly), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.user)
        self.assertEquals(len(self.user.friends), 1)
        self.mox.VerifyAll()

class MockUserFriendsHandler(UserFriendsHandler):
    def __init__(self, handler):
        self.handler = handler

    def render_html(self, user, friends, msg = None):
        self.handler.render_html(user, friends, msg)

    def render_template(self, template):
        self.handler.render_template(template)

if __name__ == '__main__':
    unittest.main()

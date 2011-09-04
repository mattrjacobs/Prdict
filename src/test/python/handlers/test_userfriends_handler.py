#!/usr/bin/env python

import logging
import mox
import simplejson as json
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

        self.set_user(self.email, False)

        self.user_2_email = "user_2@prdict.com"
        self.user_2 = self._create_user("Prdict_User_2", self.user_2_email, [User(self.email), User(self.friend_email)])

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

#    def testJson(self):
#        readJson = json.loads(self.impl.render_json(self.user_2,
#                                                    self.impl.get_entries(self.user_2)))
#        user = readJson['user']
#        self.assertEquals(user['username'], self.user_2.username)
#        self.assertEquals(user['link'], "/api/users/%s" % self.user_2.key())
##        self.assertEquals(user['friends'],
#                          "/api/users/%s/friends" % self.user_2.key())
#        self.assertEquals(user['email'], self.user_2.email)
#        self.assertTrue(len(user['updated']) > 0)
#        self.assertTrue(len(user['created']) > 0)
#        json_friend_1 = readJson['friends'][0]
#        json_friend_2 = readJson['friends'][1]        
#        if json_friend_1['username'] == self.user.username and \
#               json_friend_2['username'] == self.friend_user.username:
#            friend_1 = json_friend_1
#            friend_2 = json_friend_2
#        elif json_friend_1['username'] == self.friend_user.username and \
#               json_friend_2['username'] == self.user.username:
#            friend_1 = json_friend_2
#            friend_2 = json_friend_1
#        else:
#            self.fail()

#        self.assertEquals(friend_1['username'], self.user.username)
#        self.assertEquals(friend_1['link'], "/api/users/%s" % self.user.key())
#        self.assertEquals(friend_1['friends'],
#                          "/api/users/%s/friends" % self.user.key())
#        self.assertEquals(friend_1['email'], self.user.email)
#        self.assertTrue(len(friend_1['updated']) > 0)
#        self.assertTrue(len(friend_1['created']) > 0)

#        self.assertEquals(friend_2['username'], self.friend_user.username)
#        self.assertEquals(friend_2['link'], "/api/users/%s" % self.friend_user.key())
#        self.assertEquals(friend_2['friends'],
#                          "/api/users/%s/friends" % self.friend_user.key())
#        self.assertEquals(friend_2['email'], self.friend_user.email)
#        self.assertTrue(len(friend_2['updated']) > 0)
#        self.assertTrue(len(friend_2['created']) > 0)
            

    def testIsFormPostDataValidFalse(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : ''}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertFalse(is_valid)

    def testIsFormPostDataValidFalse(self):
        self.impl.request = self.req(json.dumps({ 'email' : ''}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertFalse(is_valid)

    def testIsFormPostDataValidUnregistered(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : 'unregistered_user@random.com'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertFalse(is_valid)

    def testIsJsonPostDataValidUnregistered(self):
        self.impl.request = self.req(json.dumps({ 'email' : 'unregistered_user@random.com'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertFalse(is_valid)

    def testIsFormPostDataValidMyself(self):
        self.impl.request = self.req(urllib.urlencode({'email' : self.email }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertFalse(is_valid)

    def testIsJsonPostDataValidMyself(self):
        self.impl.request = self.req(json.dumps({'email' : self.email }), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertFalse(is_valid)

    def testIsFormPostDataValidRegistered(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertTrue(is_valid)

    def testIsJsonPostDataValidRegistered(self):
        self.impl.request = self.req(json.dumps({ 'email' : self.friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.user)
        self.assertTrue(is_valid)

    def testHandleFormPostUserNotAFriendYet(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.non_friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(201)
        self.mock_handler.render_html(self.user, mox.Func(self.FriendsListWithNewMember), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.user)
        self.assertEquals(len(self.user.friends), 2)
        self.assertTrue(self.non_friend_user.user in map(lambda user: user, self.user.friends))
        self.mox.VerifyAll()

    def testHandleJsonPostUserNotAFriendYet(self):
        self.impl.request = self.req(json.dumps({ 'email' : self.non_friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(201)
        self.mock_handler.render_html(self.user, mox.Func(self.FriendsListWithNewMember), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.user)
        self.assertEquals(len(self.user.friends), 2)
        self.assertTrue(self.non_friend_user.user in map(lambda user: user, self.user.friends))
        self.mox.VerifyAll()

    def testHandleFormPostGAEReadOnlyErrorPropagatesUp(self):
        self.mox.StubOutWithMock(self.impl, "add_to_friends")
        
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.non_friend_email}), "POST")
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

    def testHandleJsonPostGAEReadOnlyErrorPropagatesUp(self):
        self.mox.StubOutWithMock(self.impl, "add_to_friends")
        
        self.impl.request = self.req(json.dumps({ 'email' : self.non_friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.add_to_friends(self.user, mox.IsA(User)).AndRaise(CapabilityDisabledError)
        self.mox.ReplayAll()

        exceptionRaised = False
        try:
            self.impl.handle_post(self.user)
        except CapabilityDisabledError:
            exceptionRaised = True
        self.assertTrue(exceptionRaised)
        self.mox.VerifyAll()

    def testHandleFormPostUserAlreadyFriend(self):
        self.impl.request = self.req(urllib.urlencode({ 'email' : self.friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(302)
        self.mock_handler.render_html(self.user, mox.Func(self.FriendsListWithOldMembersOnly), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.user)
        self.assertEquals(len(self.user.friends), 1)
        self.mox.VerifyAll()

    def testHandleJsonPostUserAlreadyFriend(self):
        self.impl.request = self.req(json.dumps({ 'email' : self.friend_email}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.JSON_ENCODING
        self.impl.response.set_status(302)
        self.mock_handler.render_html(self.user, mox.Func(self.FriendsListWithOldMembersOnly), mox.IgnoreArg(), mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.user)
        self.assertEquals(len(self.user.friends), 1)
        self.mox.VerifyAll()

class MockUserFriendsHandler(UserFriendsHandler):
    def __init__(self, handler):
        self.handler = handler

    def render_html(self, user, friends, msg = None, cookie_user = None):
        self.handler.render_html(user, friends, msg, cookie_user)

    def render_template(self, template):
        self.handler.render_template(template)

    def render_string(self, s):
        self.handler.render_string(s)
        

if __name__ == '__main__':
    unittest.main()

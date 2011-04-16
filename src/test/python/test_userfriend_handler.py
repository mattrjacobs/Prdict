#!/usr/bin/env python

import logging
import mox
import simplejson as json
import unittest
import urllib

from google.appengine.api.users import User
from google.appengine.ext import db
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

    def JsonFromFriend(self, friendJson):
        readJson = json.loads(friendJson)
        email_ok = self.friend_user.email == readJson['email']
        username_ok = self.friend_user.username == readJson['username']
        link_ok = "/api/users/%s" % self.friend_user.key() == readJson['link']
        friends_ok = "/api/users/%s/friends" % self.friend_user.key() == \
                     readJson['friends']
        created_ok = len(readJson['created']) > 0
        updated_ok = len(readJson['updated']) > 0
        
        return email_ok and username_ok and link_ok and friends_ok and \
            created_ok and updated_ok

    def SameUserKey(self, user):
        return str(user.key()) == self.user_key

    def SameFriendKey(self, friend):
        return str(friend.key()) == self.friend_key

    def testGetNoUser(self):
        self.remove_user()
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        
        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetInvalidUserKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get("abc", self.friend_key)
        self.mox.VerifyAll()

    def testGetInvalidFriendKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.user_key, "abc")
        self.mox.VerifyAll()

    def testGetByNonFriendUnauthorized(self):
        self.set_user(self.non_friend_email, False)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetByUserSucceeds(self):
        self.mock_handler.render_html(mox.Func(self.SameFriendKey), None)
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetByFriendSucceeds(self):
        self.set_user(self.friend_email, False)
        self.mock_handler.render_html(mox.Func(self.SameFriendKey), None)
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetByAdminSucceeds(self):
        self.set_user(self.admin_email, True)
        self.mock_handler.render_html(mox.Func(self.SameFriendKey), None)
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testJsonGetByAdminSucceeds(self):
        self.set_user(self.admin_email, True)
        self.impl.request = self.reqWithQuery("", "GET", "alt=json")
        self.mock_handler.render_string(mox.Func(self.JsonFromFriend))
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testGetNonFriend404(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.user_key, self.non_friend_key)
        self.mox.VerifyAll()

    def testDeleteAnonymous(self):
        self.remove_user()
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()
        
        self.impl.delete(self.user_key, self.friend_key)
        self.mox.VerifyAll()

    def testDeleteEmptyUserKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete("", self.friend_key)
        self.mox.VerifyAll()

    def testDeleteInvalidUserKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete("abc", self.friend_key)
        self.mox.VerifyAll()

    def testDeleteEmptyFriendKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, "")
        self.mox.VerifyAll()

    def testDeleteEmptyUserKey(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, "abc")
        self.mox.VerifyAll()

    def testDeleteSucceeds(self):
        self.mock_handler.precondition_passes(mox.Func(self.SameUserKey)).AndReturn(True)
        self.impl.response.set_status(200)
        self.mock_handler.render_html(mox.Func(self.SameUserKey), mox.StrContains("Deleted"))
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.mox.VerifyAll()
        self.assertFalse(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)

    def testDeleteSucceedsAdmin(self):
        self.set_user(self.non_friend_email, True)
        self.mock_handler.precondition_passes(mox.Func(self.SameUserKey)).AndReturn(True)
        self.impl.response.set_status(200)
        self.mock_handler.render_html(mox.Func(self.SameUserKey), mox.StrContains("Deleted"))
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.mox.VerifyAll()
        self.assertFalse(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)

    def testDeleteFailsForNonAdminFriend(self):
        self.set_user(self.friend_email, False)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.assertTrue(self.friend_user.user in self.user.friends)
        self.mox.VerifyAll()

    def testDeleteFailsForNonAdminNonFriend(self):
        self.set_user(self.non_friend_email, False)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("errors/403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.assertTrue(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)
        self.mox.VerifyAll()

    def testDeleteFailsWhenNonFriendIsDeleted(self):
        self.impl.response.set_status(404)
        self.mock_handler.render_template("errors/404.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.non_friend_key)
        self.assertTrue(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)
        self.mox.VerifyAll()

    def testDeleteFailsWhenPreconditionFails(self):
        self.mock_handler.precondition_passes(mox.Func(self.SameUserKey)).AndReturn(False)
        self.impl.response.set_status(412)
        self.mock_handler.render_html(mox.Func(self.SameUserKey), mox.StrContains("User was out of date"))
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.assertTrue(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)
        self.mox.VerifyAll()

    def testDeleteFailsWhenConflictOccurs(self):
        self.mock_handler.precondition_passes(mox.Func(self.SameUserKey)).AndRaise(db.TransactionFailedError)
        self.impl.response.set_status(409)
        self.mock_handler.render_html(mox.Func(self.SameUserKey), mox.StrContains("Delete transaction failed"))
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.assertTrue(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)
        self.mox.VerifyAll()

    def testDeleteFailsWhenGAEReadOnly(self):
        self.mock_handler.precondition_passes(mox.Func(self.SameUserKey)).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.render_html(mox.Func(self.SameUserKey), mox.StrContains("Temporarily unable to write data"))
        self.mox.ReplayAll()

        self.impl.delete(self.user_key, self.friend_key)
        self.assertTrue(self.friend_user.user in db.get(db.Key(encoded = self.user_key)).friends)
        self.mox.VerifyAll()


class MockUserSpecificFriendHandler(UserSpecificFriendHandler):
    def __init__(self, handler):
        self.handler = handler

    def precondition_passes(self, user):
        return self.handler.precondition_passes(user)

    def render_html(self, friend, msg=None):
        self.handler.render_html(friend, msg)

    def render_template(self, template, args=None):
        self.handler.render_template(template, args)

    def render_string(self, s):
        self.handler.render_string(s)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

from datetime import datetime
import logging
import mox
import unittest
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from base_mock_handler_test import BaseMockHandlerTest
from handlers.eventchat import EventChatHandler 
from models.event import Event
from models.message import Message
from utils.constants import Constants

class TestEventChatHandler(BaseMockHandlerTest):
    def setUp(self):
        BaseMockHandlerTest.setUp(self)

        self.set_user(self.username, False)
        self.new_message_content = "New Message Content"

    def tearDown(self):
        BaseMockHandlerTest.tearDown(self)

    def define_impl(self):
        self.mock_handler = self.mox.CreateMock(EventChatHandler)
        self.impl = MockEventChatHandler(self.mock_handler)
        
    def SameEventKey(self, event):
        return str(event.key()) == self.event_key

    def OldMessagesOnly(self, messages):
        return self.checkMessages(messages, [self.message_1, self.message_2])

    def MessagesWithNewMember(self, messages):
        contains_correct_number = len(messages) == 3
        msgs_w_new_content = filter(lambda msg: msg.content == self.new_message_content, messages)
        return contains_correct_number and len(msgs_w_new_content) == 1

    def checkMessages(self, actual_list, expected_list):
        key_map = map(lambda msg: msg.key(), actual_list)
        in_key_map = map(lambda msg: msg.key() in key_map, expected_list)
        for val in in_key_map:
            if not val:
                return False
        return True

    def testGetNoUser(self):
        self.remove_user()
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(None)
        self.impl.response.set_status(403)
        self.mock_handler.render_template("403.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetWithNonAdminUser(self):
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_html(mox.Func(self.SameEventKey), mox.Func(self.OldMessagesOnly), None, None, None)
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testGetWithAdminUser(self):
        self.set_user(self.username, True)
        self.mock_handler.get_prdict_user().MultipleTimes(2).AndReturn(self.user)
        self.mock_handler.render_html(mox.Func(self.SameEventKey), mox.Func(self.OldMessagesOnly), None, None, None)
        self.mox.ReplayAll()

        self.impl.get(self.event_key)
        self.mox.VerifyAll()

    def testIsPostDataValidFalse(self):
        self.impl.request = self.req(urllib.urlencode({'content' : ''}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.event)
        self.assertFalse(is_valid)

    def testIsPostDataValidTrue(self):
        self.impl.request = self.req(urllib.urlencode({'content' : 'test message'}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        (is_valid, _) = self.impl.is_post_data_valid(self.event)
        self.assertTrue(is_valid)

    def testHandlePostWithNonAdminSucceeds(self):
        self.impl.request = self.req(urllib.urlencode({'content' : self.new_message_content}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(201)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_html(mox.Func(self.SameEventKey), mox.Func(self.MessagesWithNewMember), None, None, "Added message")
        self.mox.ReplayAll()

        self.impl.handle_post(self.event)
        self.mox.VerifyAll()

    def testHandlePostWithAdminSucceeds(self):
        self.set_user(self.email, True)
        self.impl.request = self.req(urllib.urlencode({'content' : self.new_message_content}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.response.set_status(201)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_html(mox.Func(self.SameEventKey), mox.Func(self.MessagesWithNewMember), None, None, "Added message")
        self.mox.ReplayAll()

        self.impl.handle_post(self.event)
        self.mox.VerifyAll()

    def testHandlePostValidDataGAEReadOnly(self):
        self.mox.StubOutWithMock(self.impl, "create_chat")
        self.impl.request = self.req(urllib.urlencode({'content' : self.new_message_content}), "POST")
        self.impl.request.headers["Content-Type"] = Constants.FORM_ENCODING
        self.impl.create_chat(self.event).AndRaise(CapabilityDisabledError)
        self.impl.response.set_status(503)
        self.mock_handler.get_prdict_user().AndReturn(self.user)
        self.mock_handler.render_template("503.html", mox.IgnoreArg())
        self.mox.ReplayAll()

        self.impl.handle_post(self.event)
        self.assertFalse(self.impl.response.headers.has_key("Content-Location"))
        self.mox.VerifyAll()
    
class MockEventChatHandler(EventChatHandler):
    def __init__(self, handler):
        EventChatHandler.__init__(self)
        self.handler = handler
        
    def get_prdict_user(self):
        return self.handler.get_prdict_user()

    def render_template(self, template, params = None):
        self.handler.render_template(template, params)
        
    def render_html(self, parent, entries, prev_link = None, next_link = None,
                    msg = None):
        self.handler.render_html(parent, entries, prev_link, next_link, msg)

if __name__ == '__main__':
    unittest.main()

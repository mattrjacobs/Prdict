import datetime
import logging
import simplejson as json

from google.appengine.ext import db

from models.message import Message
from handlers.handler import AbstractHandler
from services.base_svc import BaseService

class MessageService(BaseService):
    def get_model(self):
        return Message

    def get_parent_ref(self):
        return "event"

    def get_entry_list_name(self):
        return "messages"

    def get_json_params(self, request):
        try:
            parsed_body = json.loads(request.body)
        except ValueError:
            return {}
        content = self.get_json_str(parsed_body, "content")
        event = self.get_event_from_request(request, self.get_json_str(parsed_body,  "event"))

        return self.__create_param_map(content, event)

    def get_form_params(self, request):
        content = self.get_form_str(request, "content")
        event = self.get_event_from_request(request, self.get_form_str(request, "event"))

        return self.__create_param_map(content, event)

    def __create_param_map(self, content, event):
        params = { }
        created = datetime.datetime.utcnow()
        author = AbstractHandler.get_prdict_user()

        if content is not None:
            params["content"] = content
        if created is not None:
            params["created_date"] = created
        if author is not None:
            params["author"] = author
        if event is not None:
            params["event"] = event

        return params

    def validate_params(self, params):
        return Message.validate_params(params)

    def create_entry_from_params(self, params):
        new_msg = Message(content = params["content"],
                          created = params["created_date"],
                          author = params["author"],
                          event = params["event"])
        new_msg.put()
        return new_msg

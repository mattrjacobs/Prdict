"""Handles requests for the resource of all events"""
from datetime import datetime
import httplib
import logging

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from auth import BaseAuthorizationHandler
from handlers.handler import AbstractHandler
from models import event
from models.abstract_model import AbstractModel
from utils.constants import Constants

class ListHandler(AbstractHandler, BaseAuthorizationHandler):
    """Handles requests for a list resource"""
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.html = "list.html"
        self.item_html = "item.html"

    def get(self):
        """Renders a list, and a template for dding a new member, if the
        requesting user is an admin"""
        user = self.get_prdict_user()
        can_write = self.is_user_authorized_to_write(user, None)
        all_items = self.get_all_items()
        now = datetime.now().strftime(ListHandler.DATE_FORMAT)
        self.render_template(self.html, { 'current_user' : user,
                                          'items' : all_items,
                                          'can_write' : can_write,
                                          'now' : now })

    def post(self):
        """Attempts to respond to a POST by adding a new item"""
        user = self.get_prdict_user()
        if not self.is_user_authorized_to_write(user, None):
            self.set_403()
            return None
        if self.get_header('Content-Type') != Constants.FORM_ENCODING:
            msg = "Must POST in %s format." % Constants.FORM_ENCODING
            self.response.set_status(httplib.UNSUPPORTED_MEDIA_TYPE)
            return self.render_template(self.html, { 'msg': msg,
                                                     'current_user' : user})
        title = self.request.get("title")
        description = self.request.get("description")
        (is_valid, error_message) = AbstractModel.validate_params(title, description)
        (are_others_valid, other_error_msg) = self.validate_other_params()
        if not is_valid or not are_others_valid:
            return self.__bad_request_template("%s, %s" % (error_message, other_error_msg))

        try:
            params = self.create_params(title, description)
            new_item = self.create_item(params)
        except CapabilityDisabledError:
            self.handle_transient_error()
            return
        item_url = "%s/%s" % (self.request.url, new_item.key())
        self.response.headers['Content-Location'] = item_url
        logging.error("NAME : %s" % new_item.get_item_name())
        self.render_template(self.item_html, { new_item.get_item_name() : new_item,
                                               'current_user' : user})

    def create_item(self, params):
        new_item = self.instantiate_new_item(params)
        new_item.put()
        self.response.set_status(httplib.CREATED)
        return new_item

    def create_params(self, title, description):
        raise Exception("Must be implementd by subclass")

    def validate_other_params(self):
        return (True, None)

    def instantiate_new_item(self, params):
        raise Exception("Must be implemented by subclass")

    def __bad_request_template(self, message):
        """Returns an HTML template explaining why item add failed"""
        self.response.set_status(httplib.BAD_REQUEST)
        return self.render_template(self.html, { 'msg' : message,
                                                 'current_user' : self.get_prdict_user()})

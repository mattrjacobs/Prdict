from google.appengine.ext import db

from datetime import datetime

import build
import dateutil
from prdict_user import PrdictUser

class AbstractModel(db.Model):
    title = db.StringProperty(required=True,multiline=False)
    description = db.StringProperty(required=False,multiline=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def validate_orig_params(params):
        """Return a (is_valid, error_message) tuple"""
        messages = []

        title = None
        description = None
        if "title" in params:
            title = params["title"]
        if "description" in params:
            description = params["description"]

        (title_valid, msg) = AbstractModel.validate_title(title)
        if not title_valid:
            messages.append(msg)
        (desc_valid, msg) = AbstractModel.validate_description(description)
        if not desc_valid:
            messages.append(msg)
        if title_valid and desc_valid:
            return (True, None)
        else:
            return (False, ','.join(messages))

    @staticmethod
    def validate_subset_orig_params(params):
        """Return a (is_valid, error_message) tuple"""
        messages = []

        title_valid = desc_valid = True
        if "title" in params:
            (title_valid, title_msg) = AbstractModel.validate_title(params["title"])
            if not title_valid:
                messages.append(title_msg)

        if "description" in params:
            (desc_valid, msg) = AbstractModel.validate_description(params["description"])
            if not desc_valid:
                messages.append(msg)
            
        if title_valid and desc_valid:
            return (True, None)
        else:
            return (False, ','.join(messages))

    @staticmethod
    def validate_title(title):
        if not title or not title.strip():
            return (False, "Must specify a non-empty 'title' parameter.")
        if len(title) > 80:
            return (False, "Title length must be less than or equal to 80 chars")
        return (True, None)
    
    @staticmethod
    def validate_description(description):
        if description and len(description) > 500:
            return (False, "Title length must be less than or equal to 500 chars")
        return (True, None)

    def get_etag(self):
        return "\"%s-%s-%s\"" % (dateutil.unix_timestamp(self.created),
                                 dateutil.unix_timestamp(self.updated),
                                 build.build_number)
    etag = property(get_etag)
    
    def get_isoformat_created(self):
        return "%sZ" % (self.created.isoformat(),)
    isoformat_created = property(get_isoformat_created)
    
    def get_isoformat_updated(self):
        return "%sZ" % (self.updated.isoformat(),)
    isoformat_updated = property(get_isoformat_updated)

    def get_relative_url(self):
        item_name = self.get_item_name()
        return "/api/%ss/%s" % (item_name, self.key())
    relative_url = property(get_relative_url)    

    def get_item_name(self):
        raise Exception("Must be overridden by subclasses")

    @staticmethod
    def validate_param(validation_result, error_msgs):
        (param_valid, param_error_result) = validation_result
        if not param_valid:
            error_msgs.append(param_error_result)
        return param_valid

    @staticmethod
    def parse_int(s):
        try:
            num = int(s)
            return True
        except ValueError:
            return False

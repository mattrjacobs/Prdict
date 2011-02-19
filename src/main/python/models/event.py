from google.appengine.ext import db

from datetime import datetime

import build
import dateutil
from prdict_user import PrdictUser

class Event(db.Model):
    title = db.StringProperty(required=True,multiline=False)
    description = db.StringProperty(required=False,multiline=True)
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    date_range = db.ListProperty(datetime)
    #possibly add related events
    #possible add interested users

    @staticmethod
    def validate_params(title, description, start_date, end_date):
        """Given event parameters, can a valid Event be constructed?
        Return a (is_valid, error_message) tuple"""
        messages = []

        (title_valid, msg) = Event.validate_title(title)
        if not title_valid:
            messages.append(msg)
        (desc_valid, msg) = Event.validate_description(description)
        if not desc_valid:
            messages.append(msg)
        (start_date_valid, msg) = Event.validate_start_date(start_date)
        if not start_date_valid:
            messages.append(msg)
        (end_date_valid, msg) = Event.validate_end_date(end_date)
        if not end_date_valid:
            messages.append(msg)
        if title_valid and desc_valid and start_date_valid and end_date_valid:
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
        if not description or not description.strip():
            return (False, "Must specify a non-empty 'description' parameter.")
        if len(description) > 500:
            return (False, "Title length must be less than or equal to 500 chars")
        return (True, None)

    @staticmethod
    def validate_start_date(start_date):
        if not start_date or not start_date.strip():
            return (False, "Must contain a non-empty 'start_date' parameter")
        if not Event.is_date_format_valid(start_date):
            return (False, "Start date is not formatted correctly - use ISO-8601")
        return (True, None)

    @staticmethod
    def validate_end_date(end_date):
        if not end_date or not end_date.strip():
            return (False, "Must contains a non-empty 'end_date' parameter")
        if not Event.is_date_format_valid(end_date):
            return (False, "End date is not formatted correctly - use ISO-8601")
        return (True, None)
    
    @staticmethod
    def is_date_format_valid(date_as_str):
        try:
            date = datetime.strptime(date_as_str, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    @staticmethod
    def convert_date_format(date_as_str):
        try:
            date = datetime.strptime(date_as_str, "%Y-%m-%d %H:%M:%S")
            return date
        except ValueError:
            return None

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
        return "/api/events/%s" % (self.key(),)
    relative_url = property(get_relative_url)    

from google.appengine.ext import db

from datetime import datetime

from abstract_model import AbstractModel

class Event(AbstractModel):
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)

    @staticmethod
    def validate_dates(start_date, end_date):
        messages = []
        (start_date_valid, msg) = Event.validate_date(start_date, "start_date")
        if not start_date_valid:
            messages.append(msg)
        (end_date_valid, msg) = Event.validate_date(end_date, "end_date")
        if not end_date_valid:
            messages.append(msg)
        if start_date_valid and end_date_valid:
            return (True, None)
        else:
            return (False, ','.join(messages))

    @staticmethod
    def validate_date(this_date, field_name):
        if not this_date or not this_date.strip():
            return (False, "Must contain a non-empty '%s' parameter" % field_name)
        if not Event.is_date_format_valid(this_date):
            return (False, "'%s' is not formatted correctly - use ISO-8601" % field_name)
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

    def get_start_date_str(self):
        return self.start_date.strftime("%Y-%m-%d %H:%M:%S")
    start_date_str = property(get_start_date_str)

    def get_end_date_str(self):
        return self.end_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = property(get_end_date_str)

    def get_item_name(self):
        return "event"
    item_name = property(get_item_name)

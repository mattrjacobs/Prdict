from abstract_model import AbstractModel

from datetime import datetime
import logging
import urllib
import simplejson as json
from utils import timezones

from google.appengine.ext import db

class EventEncoder(json.JSONEncoder):
    def default(self, event):
        if not isinstance(event, Event):
            return

        return { 'title' : event.title,
                 'description' : event.description,
                 'self' : event.relative_url,
                 'start_date' : event.start_date_str,
                 'end_date' : event.end_date_str,
                 'created' : event.isoformat_created,
                 'updated' : event.isoformat_updated }

class Event(AbstractModel):
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)

    @staticmethod
    def parse_event_uri(event_uri):
        uri_pieces = urllib.unquote(event_uri).strip("/").split("/")
        try:
            if len(uri_pieces) == 3:
                if uri_pieces[0] != "api" or uri_pieces[1] != "events":
                    return None
                event_key = uri_pieces[2]
                return db.get(db.Key(encoded = event_key))
            else:
                return None
        except db.BadKeyError:
            return None

    @staticmethod
    def validate_dates(start_date, end_date):
        messages = []
        dates_ok = True
        if not start_date:
            dates_ok = False
            messages.append("Start date was null or badly formatted")
        if not end_date:
            dates_ok = False
            messages.append("End date was null or badly formatted")
        if start_date and end_date and (end_date < start_date):
            dates_ok = False
            messages.append("End date cannot be before start date")
        if dates_ok:
            return (True, None)
        else:
            return (False, ','.join(messages))

    @staticmethod
    def validate_date(this_date, field_name):
        if not this_date or not this_date.strip():
            return (None, "Must contain a non-empty '%s' parameter" % field_name)
        try:
            date = datetime.strptime(this_date, "%Y-%m-%d %H:%M:%S")
            return (date, None)
        except ValueError:
            return (None, "'%s' is not formatted correctly - use ISO-8601" % field_name)

    @staticmethod
    def validate_params(params):
        error_msgs = []
        (are_orig_valid, orig_error_msg) = \
                         AbstractModel.validate_orig_params(params)
        start_date_str = end_date_str = None
        start_date = end_date = None

        if "start_date_str" in params:
            start_date_str = params["start_date_str"]
            (start_date, start_date_error_msg) = \
                         Event.validate_date(start_date_str, "start_date")
            if not start_date:
                error_msgs.append(start_date_error_msg)
            else:
                params["start_date"] = start_date
        if "end_date_str" in params:
            end_date_str = params["end_date_str"]
            (end_date, end_date_error_msg) = \
                       Event.validate_date(end_date_str, "end_date")
            if not end_date:
                error_msgs.append(end_date_error_msg)
            else:
                params["end_date"] = end_date

        (are_dates_valid, date_error_msg) = \
                          Event.validate_dates(start_date, end_date)
        if are_orig_valid and are_dates_valid:
            return (True, None)
        else:
            if orig_error_msg:
                error_msgs.append(orig_error_msg)
            if date_error_msg:
                error_msgs.append(date_error_msg)
            return (False, ",".join(error_msgs))

    def validate_subset_params(self, params):
        error_msgs = []
        dates_ok = True
        (are_orig_valid, orig_error_msg) = \
                         AbstractModel.validate_orig_params(params)
        start_date_str = end_date_str = None
        start_date = end_date = None

        if "start_date_str" in params:
            start_date_str = params["start_date_str"]
            (start_date, start_date_error_msg) = \
                         Event.validate_date(start_date_str, "start_date")
            if not start_date:
                error_msgs.append(start_date_error_msg)
                dates_ok = False
            else:
                params["start_date"] = start_date
        if "end_date_str" in params:
            end_date_str = params["end_date_str"]
            (end_date, error_msg) = \
                       Event.validate_date(end_date_str, "end_date")
            if not end_date:
                error_msgs.append(end_date_error_msg)
                dates_ok = False
            else:
                params["end_date"] = end_date

        if not start_date:
            start_date = self.start_date
        if not end_date:
            end_date = self.end_date

        (are_both_dates_valid, date_combo_error_msg) = \
                               Event.validate_dates(start_date, end_date)
        
        if are_orig_valid and dates_ok and are_both_dates_valid:
            return (True, None)
        else:
            if orig_error_msg:
                error_msgs.append(orig_error_msg)
            if date_combo_error_msg:
                error_msgs.append(date_combo_error_msg)
            return (False, ",".join(error_msgs))

    def get_start_date_str(self):
        return self.start_date.strftime("%Y-%m-%d %H:%M:%S")
    start_date_str = property(get_start_date_str)

    def get_end_date_str(self):
        return self.end_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = property(get_end_date_str)

    def get_nice_start_date_str(self):
        return self.start_date.strftime("%b %d %H:%M")
    nice_start_date_str = property(get_nice_start_date_str)

    def get_nice_start_date_est(self):
        return self.start_date.replace(tzinfo = timezones.UstTzInfo()).astimezone(timezones.EstTzInfo()).strftime("%b %d %I:%M %p") + " EST"
    nice_start_date_est = property(get_nice_start_date_est)

    def get_item_name(self):
        return "event"
    item_name = property(get_item_name)

    def to_json(self):
        return EventEncoder(sort_keys=True).encode(self)

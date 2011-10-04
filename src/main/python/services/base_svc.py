import dateutil
import logging
import simplejson as json
import urllib

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from models.event import Event
from models.league import League
from models.sport import Sport
from models.team import Team

def update_txn(svc, entry, params, request):
    if not svc.precondition_passes(entry, request):
        return (False, None, "Entry was out of date on update")
    else:
        updated_entry = svc.update_entry_from_params(entry, params)
        updated_entry.put()
        return (True, updated_entry, None)

def delete_txn(svc, entry, request):
    if not svc.precondition_passes(entry, request):
        return (False, "Entry was out of date on delete")
    else:
        entry.delete()
        return (True, None)

def delete_member_txn(svc, parent, entry, request):
    if not svc.precondition_passes(parent, request):
        return (False, "Parent was out-of-date on member delete")
    else:
        updated_entry = svc.delete_entry_from_parent_in_txn(parent, entry)
        updated_entry.put()
        return (True, None)

class BaseService:
    def __init__(self):
        pass

    # returns:
    # Boolean - is content type OK?
    # Boolean - are params valid to create a League instance?
    # Boolean - did DB save succeed?
    # String errorMsg - any errors encountered
    # League - new League (saved to DB)
    def create_entry(self, request, content_type):
        if content_type == "atom":
            params = self.get_atom_params(request)
        elif content_type == "json":
            params = self.get_json_params(request)
        elif content_type == "form":
            params = self.get_form_params(request)
        else:
            return (False, False, False, "Must use JSON or Form encoding", None)

        (is_valid, error_message) = self.validate_params(params)
        if not is_valid:
            return (True, False, False, error_message, None)

        try:
            new_entry = self.create_entry_from_params(params)
        except CapabilityDisabledError:
            return (True, True, False, "DB Save failed temporarily", None)

        return (True, True, True, None, new_entry)

    # returns:
    # Boolean - is content type OK?
    # Boolean - are params valid to create a League instance?
    # Boolean - did preconditions on entry succeed?
    # Boolean - did DB avoid a conflict in datastore?
    # Boolean - did DB write succeed?
    # String errorMsg - any errors encountered
    # object - edited object (saved to DB)
    def update_entry(self, current_entry, request, content_type):
        if content_type == "atom":
            params = self.get_atom_params(request)
        elif content_type == "json":
            params = self.get_json_params(request)
        elif content_type == "form":
            params = self.get_form_params(request)
        else:
            return (False, False, False, False, False,
                    "Must use JSON or Form encoding", None)

        (is_valid, error_msg) = self.validate_subset_params(current_entry, params)
        if not is_valid:
            return (True, False, False, False, False, error_msg, None)

        try:
            (preconditions_succeeded, updated_entry, txn_error_msg) = \
                                      db.run_in_transaction(
                update_txn, self, current_entry, params, request)
            if not preconditions_succeeded:
                return (True, True, False, False, False,
                        txn_error_msg, None)
        except db.TransactionFailedError:
            return (True, True, True, False, False,
                    "DB conflict on update", None)
        except CapabilityDisabledError:
            return (True, True, True, True, False,
                    "DB Save failed temporarily", None)

        return (True, True, True, True, True, None, updated_entry)

    # returns:
    # Boolean - did preconditions on entry succeed?
    # Boolean - did DB avoid a conflict in datastore?
    # Boolean - did DB write succeed?
    # String - errorMsg
    def delete_entry(self, entry, request):
        try:
            (preconditions_succeeded, txn_error_msg) = \
                                      db.run_in_transaction(
                delete_txn, self, entry, request)
            if not preconditions_succeeded:
                return (False, False, False, txn_error_msg)
        except db.TransactionFailedError:
            return (True, False, False, "DB conflict on Delete")
        except CapabilityDisabledError:
            return (True, True, False, "DB Delete failed temporarily")

        return (True, True, True, None)

    def delete_entry_from_parent(self, parent, entry, request):
        try:
            (preconditions_succeeded, txn_error_msg) = \
                                      db.run_in_transaction(
                delete_member_txn, self, parent, entry, request)
            if not preconditions_succeeded:
                return (False, False, False, txn_error_msg)
        except db.TransactionFailedError:
            return (True, False, False, "DB conflict on member delete from list")
        except CapabilityDisabledError:
            return (True, True, False, "DB Member Delete failed temporarily")

        return (True, True, True, None)

    def get_atom_params(self, request):
        raise "Not implemented yet"

    def get_json_params(self, request):
        raise "Must be implemented by subclasses"

    def get_form_params(self, request):
        raise "Must be implemented by subclasses"

    def validate_params(self, params):
        raise "Must be implemented by subclasses"

    def validate_subset_params(self, entry, params):
        raise "Must be implemented by subclasses"

    def create_entry_from_params(self, params):
        raise "Must be implemented by subclasses"

    def update_entry_from_params(self, entry, params):
        raise "Must be implemented by subclasses"

    def delete_entry_from_parent_in_txn(self, parent, entry):
        raise "Must be implemented by subclasses"

    def get_form_str(self, request, field_name):
        return request.get(field_name, default_value = None)

    def get_json_str(self, parsed_json, field_name):
        if field_name in parsed_json:
            return parsed_json[field_name]
        else:
            return None

    def precondition_passes(self, entry, request):
        """All conditional clauses must pass on a conditional request,
        if multiple are specified (although this would be an odd
        thing for a client to do)."""
        if 'If-Match' in request.headers:
            req_etags = map(lambda s: s.strip(),
                            request.headers['If-Match'].split(','))
            if '*' in req_etags and entry is None:
                return False
            if entry.etag not in req_etags:
                return False
        if 'If-None-Match' in request.headers:
            req_etags = map(lambda s: s.strip(),
                            request.headers['If-None-Match'].split(','))
            if '*' in req_etags and entry is not None:
                return False
            if entry.etag in req_etags:
                return False
        if 'If-Unmodified-Since' in request.headers:
            req_lm = dateutil.parse_http_date(
                request.headers['If-Unmodified-Since'])
            if req_lm and dateutil.normalize(entry.updated) > req_lm:
                return False
        if 'If-Modified-Since' in request.headers:
            req_lm = dateutil.parse_http_date(
                request.headers['If-Modified-Since'])
            if req_lm and dateutil.normalize(entry.updated) <= req_lm:
                return False
        return True

    def get_league_from_request(self, request, league_param):
        return self.__parse_from_uri_and_params(request, "leagues", league_param,
                                                League.parse_league_uri)
    def get_sport_from_request(self, request, sport_param):
        return self.__parse_from_uri_and_params(request, "sports", sport_param,
                                                Sport.parse_sport_uri)

    def get_event_from_request(self, request, event_param):
        return self.__parse_from_uri_and_params(request, "events", event_param,
                                                Event.parse_event_uri)

    def parse_date(self, date_str):
        (date, error_msgs) = Event.validate_date(date_str, "date field")
        return date

    def __parse_from_uri_and_params(self, request, uri_element,
                                    param, validation_func):
        param_from_uri = None
        url_pieces = request.path.split("/")
        if uri_element in url_pieces:
            idx = url_pieces.index(uri_element)
            if len(url_pieces) > idx + 1:
                key = url_pieces[idx + 1]
                try:
                    obj = db.get(db.Key(encoded = key))
                    param_from_uri = obj
                except db.BadKeyError:
                    return None
        if param and param_from_uri:
            parsed_param = validation_func(param)
            if str(parsed_param.key()) != str(param_from_uri.key()):
                return None
            else:
                return parsed_param
        elif param:
            return validation_func(param)
        elif param_from_uri:
            return param_from_uri
        else:
            return None

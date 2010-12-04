"""Handles request for a user resource"""
import httplib
import logging

from handlers.auth import FriendsAuthorizationHandler
from handlers.entry import EntryHandler

def delete_txn(handler, user, friend):
    """Wraps a DB delete triggered by HTTP DELETE in txn"""
    if not user or not friend:
        return (None, None, None)
    if not handler.precondition_passes(user):
        status = httplib.PRECONDITION_FAILED
        msg = "User was out of date"
    user.friends.remove(friend.user)
    user.put()
    return (user, httplib.OK, "Deleted friend %s" % friend.username)

class UserSpecificFriendHandler(EntryHandler, FriendsAuthorizationHandler):
    """Handles an HTTP request for a PrdictUser resource
    by checking in a given user's friend list.
    EntryHandler handles request parsing
    FriendsAuthorizationHandler handles authorization logic"""
    def render_html(self, entry, msg=None):
        current_user = self.get_prdict_user()
        self.render_template('user.html', { 'msg' : msg,
                                            'current_user' : current_user,
                                            'user' : entry })

    def render_atom(self, entry):
        self.render_template('xml/user_atom.xml',
                             { 'user' : entry,
                               'base_url' : self.baseurl() } )

    def render_json(self, entry):
        self.render_template('json/user_json.xml',
                             { 'user' : entry,
                               'base_url' : self.baseurl() } )

    def get(self, user_key, friend_key):
        user = self.get_authorized_entry(user_key, "read")
        if not user:
            return
        friend = self.get_entry(friend_key)
        if not friend:
            self.set_404()
            return
        if not friend.user in user.friends:
            self.set_404()
            return
        
        self.handle_http_caching_headers(user)
        self.handle_output(friend)
        
    def post(self, user_key, friend_key):
        self.allow_overloaded_post_of_delete(key)

    def put(self, key):
        return self.response.set_status(httplib.METHOD_NOT_ALLOWED)

    def delete(self, user_key, friend_key):
        user_before_membership_delete = self.get_authorized_entry(user_key, "write")
        if not user_before_membership_delete:
            return
        friend = self.get_authorized_entry(friend_key, "read")
        if not friend:
            return
        
        if not friend.user in user.friends:
            self.set_404()
            return
        try:
            entry, status, msg = \
                   db.run_in_transaction(delete_txn, self,
                                         user_before_membership_delete, friend)
        except db.TransactionFailedError:
            user = user_before_membership_delete
            status = httplib.CONFLICT
            msg = "Delete transaction failed"
        except CapabilityDisabledError:
            user = user_before_membership_delete
            status = httplib.SERVICE_UNAVAILABLE
            msg = "Unabled to write data."
        if status is None:
            return
        self.response.set_status(status)
        self.render_html(user, msg)

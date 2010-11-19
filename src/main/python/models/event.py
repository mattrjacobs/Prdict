from google.appengine.ext import db

from prdict_user import PrdictUser

class Event(db.Model):
    title = db.StringProperty(required=True,multiline=False)
    description = db.StringProperty(required=False,multiline=True)
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    #possibly add related events
    #possible add interested users

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

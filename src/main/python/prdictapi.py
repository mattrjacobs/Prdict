from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers.event import EventHandler
from handlers.eventchat import EventChatHandler
from handlers.events import EventsHandler
from handlers.home import HomeHandler
from handlers.user import UserHandler
from handlers.userfriend import UserSpecificFriendHandler
from handlers.userfriends import UserFriendsHandler
from handlers.users import UsersHandler
from handlers.version import VersionHandler

urlmap = [('/', HomeHandler),
          ('/api/events', EventsHandler),
          (r'/api/events/([^/]+)', EventHandler),
          (r'/api/events/([^/]+)/chat', EventChatHandler),
          ('/api/users', UsersHandler),
          (r'/api/users/([^/]+)', UserHandler),
          (r'/api/users/([^/]+)/friends', UserFriendsHandler),
          (r'/api/users/([^/]+)/friends/([^/]+)', UserSpecificFriendHandler),
          ('/version', VersionHandler)]
application = webapp.WSGIApplication(urlmap, debug=True)

def main():
    run_wsgi_app(application)
        
if __name__ == "__main__":
    main()

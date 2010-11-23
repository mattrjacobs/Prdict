from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers.event import EventHandler
from handlers.events import EventsHandler
from handlers.home import HomeHandler
from handlers.user import UserHandler
from handlers.users import UsersHandler
from handlers.version import VersionHandler

urlmap = [('/', HomeHandler),
          ('/api/events', EventsHandler),
          (r'/api/events/([^/]+)', EventHandler),
          ('/api/users', UsersHandler),
          (r'/api/users/([^/]+)', UserHandler),
          ('/version', VersionHandler)]
application = webapp.WSGIApplication(urlmap, debug=True)

def main():
    run_wsgi_app(application)
        
if __name__ == "__main__":
    main()

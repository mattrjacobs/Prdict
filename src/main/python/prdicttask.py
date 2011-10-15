from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers.task.mark_uncancelled import MarkUncancelledTaskHandler
from handlers.task.scoreupdate import ScoreUpdateTaskHandler

urlmap = [('/task/score_update', ScoreUpdateTaskHandler),
          ('/task/mark_uncancelled', MarkUncancelledTaskHandler)]
application = webapp.WSGIApplication(urlmap, debug=True)

def main():
    run_wsgi_app(application)
        
if __name__ == "__main__":
    main()

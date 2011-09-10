from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers.task.scoreupdate import ScoreUpdateTaskHandler

urlmap = [('/task/score_update', ScoreUpdateTaskHandler)]
application = webapp.WSGIApplication(urlmap, debug=True)

def main():
    run_wsgi_app(application)
        
if __name__ == "__main__":
    main()

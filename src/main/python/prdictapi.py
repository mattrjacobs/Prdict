from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers.dev.data_populate import DevDataPopulateHandler
from handlers.event import EventHandler
from handlers.eventchat import EventChatHandler
from handlers.events import EventsHandler
from handlers.events_recent import RecentEventsHandler
from handlers.events_future import FutureEventsHandler
from handlers.events_inprogress import InProgressEventsHandler
from handlers.home import HomeHandler
from handlers.league import LeagueHandler
from handlers.leagues import LeaguesHandler
from handlers.league_member import LeagueMemberHandler
from handlers.league_season import LeagueSeasonMemberHandler
from handlers.league_seasons import LeagueSeasonsHandler
from handlers.league_teams import LeagueTeamsHandler
from handlers.sport import SportHandler
from handlers.sports import SportsHandler
from handlers.sport_leagues import SportLeaguesHandler
from handlers.team import TeamHandler
from handlers.teams import TeamsHandler
from handlers.team_member import TeamMemberHandler
from handlers.team_schedule import TeamScheduleHandler
from handlers.ui.eventchat import EventChatUiHandler
from handlers.ui.league import LeagueUiHandler
from handlers.ui.team import TeamUiHandler
from handlers.ui.team_schedule import TeamScheduleUiHandler
from handlers.user import UserHandler
from handlers.userfriend import UserSpecificFriendHandler
from handlers.userfriends import UserFriendsHandler
from handlers.users import UsersHandler
from handlers.version import VersionHandler

from handlers.temporary import TempTeamsAddHandler

#from gae_mini_profiler import profiler

import os
from google.appengine.dist import use_library

urlmap = [('/', HomeHandler),
          ('/temp/teams-add', TempTeamsAddHandler),
          ('/api/events', EventsHandler),
          ('/api/events/recent', RecentEventsHandler),
          ('/api/events/inprogress', InProgressEventsHandler),
          ('/api/events/future', FutureEventsHandler),
          (r'/api/events/([^/]+)', EventHandler),
          (r'/api/events/([^/]+)/chat', EventChatHandler),
          ('/api/leagues', LeaguesHandler),
          (r'/api/leagues/([^/]+)', LeagueHandler),
          (r'/api/leagues/([^/]+)/seasons', LeagueSeasonsHandler),
          (r'/api/leagues/([^/]+)/seasons/([^/]+)', LeagueSeasonMemberHandler),
          (r'/api/leagues/([^/]+)/teams', LeagueTeamsHandler),
          (r'/api/leagues/([^/]+)/teams/([^/]+)', TeamMemberHandler),
          ('/api/sports', SportsHandler),
          (r'/api/sports/([^/]+)', SportHandler),
          (r'/api/sports/([^/]+)/leagues', SportLeaguesHandler),
          (r'/api/sports/([^/]+)/leagues/([^/]+)', LeagueMemberHandler),
          ('/api/teams', TeamsHandler),
          (r'/api/teams/([^/]+)', TeamHandler),
          (r'/api/teams/([^/]+)/seasons/([^/]+)/schedule', TeamScheduleHandler),
          ('/api/users', UsersHandler),
          (r'/api/users/([^/]+)', UserHandler),
          (r'/api/users/([^/]+)/friends', UserFriendsHandler),
          (r'/api/users/([^/]+)/friends/([^/]+)', UserSpecificFriendHandler),
          ('/dev/populate', DevDataPopulateHandler),
          (r'/events/([^/]+)/chat', EventChatUiHandler),
          (r'/leagues/([^/]+)', LeagueUiHandler),
          (r'/leagues/([^/]+)/teams/([^/]+)', TeamUiHandler),
          (r'/leagues/([^/]+)/teams/([^/]+)/seasons/([^/]+)/schedule', TeamScheduleUiHandler),
          ('/version', VersionHandler)]
#application = profiler.ProfilerWSGIMiddleware(webapp.WSGIApplication(urlmap, debug=True))
application = webapp.WSGIApplication(urlmap, debug=True)

def main():
    run_wsgi_app(application)
        
if __name__ == "__main__":
    main()

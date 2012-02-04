from handlers.handler import AbstractHandler

from datetime import datetime
from datetime import timedelta
import logging
import random

from google.appengine.api import users
from google.appengine.ext import db

from models import event
from models import league
from models import prdict_user
from models import sport
from models.team import Team

class DevDataPopulateHandler(AbstractHandler):
    def get(self):
        new_users = []
        new_events = []
        new_sports = []
        new_leagues = []
        new_teams = []

        if self.is_dev_host():
            baseball = sport.Sport(title = 'Baseball')
            basketball = sport.Sport(title = 'Basketball')
            football = sport.Sport(title = 'Football')
            hockey = sport.Sport(title = 'Hockey')
            baseball.put()
            basketball.put()
            football.put()
            hockey.put()

            nba = league.League(title = "NBA", sport = basketball,
                                parent = basketball)
            nbdl = league.League(title = "NBDL", sport = basketball,
                                 parent = basketball)
            mlb = league.League(title = "MLB", sport = baseball,
                                parent = baseball)
            aaa = league.League(title = "AAA", sport = baseball,
                                parent = baseball)
            nfl = league.League(title = "NFL", sport = football,
                                parent = football)
            cfl = league.League(title = "CFL", sport = football,
                                parent = football)
            nhl = league.League(title = "NHL", sport = hockey,
                                parent = hockey)
            nba.put()
            nbdl.put()
            mlb.put()
            aaa.put()
            nfl.put()
            cfl.put()
            nhl.put()

            self.create_nba_teams(nba)
            self.create_nbdl_teams(nbdl)
            self.create_mlb_teams(mlb)
            self.create_aaa_teams(aaa)
            self.create_nfl_teams(nfl)
            self.create_cfl_teams(cfl)
            self.create_nhl_teams(nhl)
                        
            for i in range(0, 10):
                user = prdict_user.PrdictUser(username = "user_%d" % i,
                                              user = users.User("user_%d@testprdict.com" % i))
                user.friends = []
                for j in range(0, i):
                    friend_email = "user_%d@testprdict.com" % j
                    user.friends.append(users.User(friend_email))
                user.put()
                new_users.append(user)
                
                rnd_for_start = random.randint(0, 100) - 50
                rnd_for_end = random.randint(0, 100)
                now = datetime.utcnow()
                start_date = now + timedelta(hours = rnd_for_start)
                end_date = start_date + timedelta(hours = rnd_for_end)
                new_event = event.Event(title = "Event_%d" % i,
                                        description = "Description_%d" % i,
                                        start_date = start_date,
                                        end_date = end_date)
                new_event.put()
                new_events.append(new_event)

        self.render_template("devPopulate.html",
                             { 'users' : new_users,
                               'events' : new_events,
                               'sports' : [baseball, basketball, football, hockey]})


    def create_nba_teams(self, nba):
        nba_teams = []
        nba_teams.append(Team(title = "Bulls", location = "Chicago",
                              logo_url = "/img/logos/nba/chicago_bulls.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Heat", location = "Miami",
                              logo_url = "/img/logos/nba/miami_heat.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Celtics", location = "Boston",
                              logo_url = "/img/logos/nba/boston_celtics.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Magic", location = "Orlando",
                              logo_url = "/img/logos/nba/orlando_magic.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Hawks", location = "Atlanta",
                              logo_url = "/img/logos/nba/atlanta_hawks.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Knicks", location = "New York",
                              logo_url = "/img/logos/nba/newyork_knicks.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "76ers", location = "Philadelphia",
                              logo_url = "/img/logos/nba/philadelphia_76ers.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Pacers", location = "Indiana",
                              logo_url = "/img/logos/nba/indiana_pacers.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Bucks", location = "Milwaukee",
                              logo_url = "/img/logos/nba/milwaukee_bucks.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Bobcats", location = "Charlotte",
                              logo_url = "/img/logos/nba/charlotte_bobcats.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Pistons", location = "Detroit",
                              logo_url = "/img/logos/nba/detroit_pistons.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Nets", location = "New Jersey",
                              logo_url = "/img/logos/nba/newjersey_nets.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Wizards", location = "Washington",
                              logo_url = "/img/logos/nba/washington_wizards.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Raptors", location = "Toronto",
                              logo_url = "/img/logos/nba/toronto_raptors.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Cavaliers", location = "Cleveland",
                              logo_url = "/img/logos/nba/cleveland_cavaliers.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Spurs", location = "San Antonio",
                              logo_url = "/img/logos/nba/sanantonio_spurs.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Lakers", location = "Los Angeles",
                              logo_url = "/img/logos/nba/losangeles_lakers.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Mavericks", location = "Dallas",
                              logo_url = "/img/logos/nba/dallas_mavericks.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Thunder", location = "Oklahoma City",
                              logo_url = "/img/logos/nba/oklahomacity_thunder.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Nuggets", location = "Denver",
                              logo_url = "/img/logos/nba/denver_nuggets.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Trailblazers", location = "Portland",
                              logo_url = "/img/logos/nba/portland_trailblazers.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Hornets", location = "New Orleans",
                              logo_url = "/img/logos/nba/neworleans_hornets.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Grizzlies", location = "Memphis",
                              logo_url = "/img/logos/nba/memphis_grizzlies.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Rockets", location = "Houston",
                              logo_url = "/img/logos/nba/houston_rockets.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Suns", location = "Phoenix",
                              logo_url = "/img/logos/nba/phoenix_suns.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Jazz", location = "Utah",
                              logo_url = "/img/logos/nba/utah_jazz.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Warriors", location = "Golden State",
                              logo_url = "/img/logos/nba/goldenstate_warriors.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Clippers", location = "Los Angeles",
                              logo_url = "/img/logos/nba/losangeles_clippers.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Kings", location = "Sacramento",
                              logo_url = "/img/logos/nba/sacramento_kings.png",
                              league=nba, parent = nba))
        nba_teams.append(Team(title = "Timberwolves", location = "Minnesota",
                              logo_url = "/img/logos/nba/minnesota_timberwolves.png",
                              league=nba, parent = nba))
        [team.put() for team in nba_teams]
    
    def create_nbdl_teams(self, nbdl):
        nbdl_teams = []
        nbdl_teams.append(Team(title = "Toros", location = "Austin",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Jam", location = "Bakersfield",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Wizards", location = "Dakota",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "BayHawks", location = "Erie",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Mad Ants", location = "Fort Wayne",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Stampede", location = "Idaho",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Energy", location = "Iowa",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Red Claws", location = "Maine",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "T-birds", location = "New Mexico",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Big Horns", location = "Reno",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Valley Vipers", location = "Rio Grande",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Skyforce", location = "Sioux Falls",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Armor", location = "Springfield",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Legends", location = "Texas",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "66ers", location = "Tulsa",
                               league = nbdl, parent = nbdl))
        nbdl_teams.append(Team(title = "Flash", location = "Utah",
                               league = nbdl, parent = nbdl))
        [team.put() for team in nbdl_teams]
        
    def create_mlb_teams(self, mlb):
        mlb_teams = []
        mlb_teams.append(Team(title = "Yankees", location = "New York",
                              logo_url="/img/logos/mlb/newyork_yankees.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Blue Jays", location = "Toronto",
                              logo_url="/img/logos/mlb/toronto_bluejays.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Orioles", location = "Baltimore",
                              logo_url="/img/logos/mlb/baltimore_orioles.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Rays", location = "Tampa Bay",
                              logo_url="/img/logos/mlb/tampabay_rays.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Red Sox", location = "Boston",
                              logo_url="/img/logos/mlb/boston_redsox.png",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Indians", location = "Cleveland",
                              logo_url="/img/logos/mlb/cleveland_indians.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Royals", location = "Kansas City",
                              logo_url="/img/logos/mlb/kansascity_royals.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "White Sox", location = "Chicago",
                              logo_url="/img/logos/mlb/chicago_whitesox.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Tigers", location = "Detroit",
                              logo_url="/img/logos/mlb/detroit_tigers.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Twins", location = "Minnesota",
                              logo_url="/img/logos/mlb/minnesota_twins.png",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Rangers", location = "Texas",
                              logo_url="/img/logos/mlb/texas_rangers.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Angels", location = "Los Angeles",
                              logo_url="/img/logos/mlb/losangeles_angels.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Athletics", location = "Oakland",
                              logo_url="/img/logos/mlb/oakland_athletics.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Mariners", location = "Seattle",
                              logo_url="/img/logos/mlb/seattle_mariners.png",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Phillies", location = "Philadelphia",
                              logo_url="/img/logos/mlb/philadelphia_phillies.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Marlins", location = "Florida",
                              logo_url="/img/logos/mlb/florida_marlins.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Nationals", location = "Washington",
                              logo_url="/img/logos/mlb/washington_nationals.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Braves", location = "Atlanta",
                              logo_url="/img/logos/mlb/atlanta_braves.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Mets", location = "New York",
                              logo_url="/img/logos/mlb/newyork_mets.png",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Reds", location = "Cincinnati",
                              logo_url="/img/logos/mlb/cincinnati_reds.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Brewers", location = "Milwaukee",
                              logo_url="/img/logos/mlb/milwaukee_brewers.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Cardinals", location = "St. Louis",
                              logo_url="/img/logos/mlb/stlouis_cardinals.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Cubs", location = "Chicago",
                              logo_url="/img/logos/mlb/chicago_cubs.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Pirates", location = "Pittsburgh",
                              logo_url="/img/logos/mlb/pittsburgh_pirates.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Astros", location = "Houston",
                              logo_url="/img/logos/mlb/houston_astros.png",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Rockies", location = "Colorado",
                              logo_url="/img/logos/mlb/colorado_rockies.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Giants", location = "San Francisco",
                              logo_url="/img/logos/mlb/sanfrancisco_giants.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Padres", location = "San Diego",
                              logo_url="/img/logos/mlb/sandiego_padres.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Dodgers", location = "Los Angeles",
                              logo_url="/img/logos/mlb/losangeles_dodgers.png",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Diamondbacks", location = "Arizona",
                              logo_url="/img/logos/mlb/arizona_diamondbacks.png",
                              league = mlb, parent = mlb))
        [team.put() for team in mlb_teams]
        
    def create_aaa_teams(self, aaa):
        aaa_teams = []
        aaa_teams.append(Team(title = "Barons", location = "Scranton/Wilkes-Barre",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Chiefs", location = "Syracuse",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "IronPigs", location = "Lehigh Valley",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Bison", location = "Buffalo",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Red Sox", location = "Pawtucket",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Red Wings", location = "Rochester",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Bulls", location = "Durham",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Knights", location = "Charlotte",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Braves", location = "Gwinnett",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Tides", location = "Norfolk",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Bats", location = "Louisville",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Clippers", location = "Columbus",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Mud Hens", location = "Toledo",
                              league = aaa, parent = aaa))
        aaa_teams.append(Team(title = "Indians", location = "Indianapolis",
                              league = aaa, parent = aaa))
        [team.put() for team in aaa_teams]
        
    def create_nfl_teams(self, nfl):
        nfl_teams = []
        nfl_teams.append(Team(title = "Colts", location = "Indianapolis",
                              logo_url="/img/logos/nfl/indianapolis_colts.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Jaguars", location = "Jacksonville",
                              logo_url="/img/logos/nfl/jacksonville_jaguars.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Titans", location = "Tennessee",
                              logo_url="/img/logos/nfl/tennessee_titans.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Texans", location = "Houston",
                              logo_url="/img/logos/nfl/houston_texans.png",
                              league = nfl, parent = nfl))
        
        nfl_teams.append(Team(title = "Chiefs", location = "Kansas City",
                              logo_url="/img/logos/nfl/kansascity_chiefs.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Raiders", location = "Oakland",
                              logo_url="/img/logos/nfl/oakland_raiders.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Broncos", location = "Denver",
                              logo_url="/img/logos/nfl/denver_broncos.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Chargers", location = "San Diego",
                              logo_url="/img/logos/nfl/sandiego_chargers.png",
                              league = nfl, parent = nfl))
        
        nfl_teams.append(Team(title = "Patriots", location = "New England",
                              logo_url="/img/logos/nfl/newengland_patriots.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Jets", location = "New York",
                              logo_url="/img/logos/nfl/newyork_jets.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Dolphins", location = "Miami",
                              logo_url="/img/logos/nfl/miami_dolphins.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Bills", location = "Buffalo",
                              logo_url="/img/logos/nfl/buffalo_bills.png",
                              league = nfl, parent = nfl))
        
        nfl_teams.append(Team(title = "Bengals", location = "Cincinnati",
                              logo_url="/img/logos/nfl/cincinnati_bengals.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Browns", location = "Cleveland",
                              logo_url="/img/logos/nfl/cleveland_browns.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Steelers", location = "Pittsburgh",
                              logo_url="/img/logos/nfl/pittsburgh_steelers.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Ravens", location = "Baltimore",
                              logo_url="/img/logos/nfl/baltimore_ravens.png",
                              league = nfl, parent = nfl))
        
        nfl_teams.append(Team(title = "Redskins", location = "Washington",
                              logo_url="/img/logos/nfl/washington_redskins.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Cowboys", location = "Dallas",
                              logo_url="/img/logos/nfl/dallas_cowboys.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Giants", location = "New York",
                              logo_url="/img/logos/nfl/newyork_giants.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Eagles", location = "Philadelphia",
                              logo_url="/img/logos/nfl/philadelphia_eagles.png",
                              league = nfl, parent = nfl))

        nfl_teams.append(Team(title = "Vikings", location = "Minnesota",
                              logo_url="/img/logos/nfl/minnesota_vikings.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Lions", location = "Detroit",
                              logo_url="/img/logos/nfl/detroit_lions.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Bears", location = "Chicago",
                              logo_url="/img/logos/nfl/chicago_bears.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Packers", location = "Green Bay",
                              logo_url="/img/logos/nfl/greenbay_packers.png",
                              league = nfl, parent = nfl))
        
        nfl_teams.append(Team(title = "49ers", location = "San Francisco",
                              logo_url="/img/logos/nfl/sanfrancisco_49ers.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Seahawks", location = "Seattle",
                              logo_url="/img/logos/nfl/seattle_seahawks.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Rams", location = "St. Louis",
                              logo_url="/img/logos/nfl/stlouis_rams.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Cardinals", location = "Arizona",
                              logo_url="/img/logos/nfl/arizona_cardinals.png",
                              league = nfl, parent = nfl))
        
        nfl_teams.append(Team(title = "Saints", location = "New Orleans",
                              logo_url="/img/logos/nfl/neworleans_saints.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Falcons", location = "Atlanta",
                              logo_url="/img/logos/nfl/atlanta_falcons.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Buccaneers", location = "Tampa Bay",
                              logo_url="/img/logos/nfl/tampabay_buccaneers.png",
                              league = nfl, parent = nfl))
        nfl_teams.append(Team(title = "Panthers", location = "Carolina",
                              logo_url="/img/logos/nfl/carolina_panthers.png",
                              league = nfl, parent = nfl))
        [team.put() for team in nfl_teams]
        
    def create_cfl_teams(self, cfl):
        cfl_teams = []
        cfl_teams.append(Team(title = "Stampeders", location = "Calgary",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Roughriders", location = "Saskatchewan",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Lions", location = "BC",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Eskimos", location = "Edmonton",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Alouettes", location = "Montreal",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Tiger Cats", location = "Hamilton",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Argonauts", location = "Toronto",
                              league = cfl, parent = cfl))
        cfl_teams.append(Team(title = "Blue Bombers", location = "Winnipeg",
                              league = cfl, parent = cfl))
        [team.put() for team in cfl_teams]

    def create_nhl_teams(self, nhl):
        nhl_teams = []
        nhl_teams.append(Team(title = "Rangers", location = "New York",
                              logo_url = "/img/logos/nhl/newyork_rangers.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Flyers", location = "Philadelphia",
                              logo_url = "/img/logos/nhl/philadelphia_flyers.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Penguins", location = "Pittsburgh",
                              logo_url = "/img/logos/nhl/pittsburgh_penguins.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Devils", location = "New Jersey",
                              logo_url = "/img/logos/nhl/newjersey_devils.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Islanders", location = "New York",
                              logo_url = "/img/logos/nhl/newyork_islanders.png",
                              league = nhl, parent = nhl))

        nhl_teams.append(Team(title = "Bruins", location = "Boston",
                              logo_url = "/img/logos/nhl/boston_bruins.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Senators", location = "Ottawa",
                              logo_url = "/img/logos/nhl/ottawa_senators.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Maple Leafs", location = "Toronto",
                              logo_url = "/img/logos/nhl/toronto_mapleleafs.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Sabres", location = "Buffalo",
                              logo_url = "/img/logos/nhl/buffalo_sabres.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Canadiens", location = "Montreal",
                              logo_url = "/img/logos/nhl/montreal_canadiens.png",
                              league = nhl, parent = nhl))

        nhl_teams.append(Team(title = "Panthers", location = "Florida",
                              logo_url = "/img/logos/nhl/florida_panthers.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Capitals", location = "Washington",
                              logo_url = "/img/logos/nhl/washington_capitals.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Jets", location = "Winnipeg",
                              logo_url = "/img/logos/nhl/winnipeg_jets.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Lightning", location = "Tampa Bay",
                              logo_url = "/img/logos/nhl/tampabay_lightning.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Hurricanes", location = "Carolina",
                              logo_url = "/img/logos/nhl/carolina_hurricanes.png",
                              league = nhl, parent = nhl))

        nhl_teams.append(Team(title = "Red Wings", location = "Detroit",
                              logo_url = "/img/logos/nhl/detroit_redwings.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Predators", location = "Nashville",
                              logo_url = "/img/logos/nhl/nashville_predators.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Blues", location = "St. Louis",
                              logo_url = "/img/logos/nhl/stlouis_blues.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Blackhawks", location = "Chicago",
                              logo_url = "/img/logos/nhl/chicago_blackhawks.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Blue Jackets", location = "Columbus",
                              logo_url = "/img/logos/nhl/columbus_bluejackets.png",
                              league = nhl, parent = nhl))

        nhl_teams.append(Team(title = "Canucks", location = "Vancouver",
                              logo_url = "/img/logos/nhl/vancouver_canucks.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Wild", location = "Minnesota",
                              logo_url = "/img/logos/nhl/minnesota_wild.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Avalanche", location = "Colorado",
                              logo_url = "/img/logos/nhl/colorado_avalanche.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Flames", location = "Calgary",
                              logo_url = "/img/logos/nhl/calgary_flames.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Oilers", location = "Edmonton",
                              logo_url = "/img/logos/nhl/edmonton_oilers.png",
                              league = nhl, parent = nhl))

        nhl_teams.append(Team(title = "Sharks", location = "San Jose",
                              logo_url = "/img/logos/nhl/sanjose_sharks.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Kings", location = "Los Angeles",
                              logo_url = "/img/logos/nhl/losangeles_kings.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Stars", location = "Dallas",
                              logo_url = "/img/logos/nhl/dallas_stars.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Coyotes", location = "Phoenix",
                              logo_url = "/img/logos/nhl/phoenix_coyotes.png",
                              league = nhl, parent = nhl))
        nhl_teams.append(Team(title = "Mighty Ducks", location = "Anaheim",
                              logo_url = "/img/logos/nhl/anaheim_mightyducks.png",
                              league = nhl, parent = nhl))
        
        
        [team.put() for team in nhl_teams]

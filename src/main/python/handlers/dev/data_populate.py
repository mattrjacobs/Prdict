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
            baseball.put()
            basketball.put()
            football.put()

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
            nba.put()
            nbdl.put()
            mlb.put()
            aaa.put()
            nfl.put()
            cfl.put()

            self.create_nba_teams(nba)
            self.create_nbdl_teams(nbdl)
            self.create_mlb_teams(mlb)
            self.create_aaa_teams(aaa)
            self.create_nfl_teams(nfl)
            self.create_cfl_teams(cfl)
                        
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
                               'sports' : [baseball, basketball, football]})


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
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Blue Jays", location = "Toronto",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Orioles", location = "Baltimore",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Rays", location = "Tampa Bay",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Red Sox", location = "Boston",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Indians", location = "Cleveland",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Royals", location = "Kansas City",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "White Sox", location = "Chicago",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Tigers", location = "Detroit",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Twins", location = "Minnesota",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Rangers", location = "Texas",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Angels", location = "Los Angeles",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Athletics", location = "Oakland",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Mariners", location = "Seattle",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Phillies", location = "Philadelphia",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Marlins", location = "Florida",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Nationals", location = "Washington",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Braves", location = "Atlanta",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Mets", location = "New York",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Reds", location = "Cincinnati",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Brewers", location = "Milwaukee",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Cardinals", location = "St. Louis",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Cubs", location = "Chicago",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Pirates", location = "Pittsburgh",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Astros", location = "Houston",
                              league = mlb, parent = mlb))
        
        mlb_teams.append(Team(title = "Rockies", location = "Colorado",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Giants", location = "San Francisco",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Padres", location = "San Diego",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Dodgers", location = "Los Angeles",
                              league = mlb, parent = mlb))
        mlb_teams.append(Team(title = "Diamondbacks", location = "Arizona",
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
        colts = Team(title = "Colts", location = "Indianapolis",
                     league = nfl, parent = nfl)
        colts.put()
        jaguars = Team(title = "Jaguars", location = "Jacksonville",
                       league = nfl, parent = nfl)
        jaguars.put()
        titans = Team(title = "Titans", location = "Tennessee",
                      league = nfl, parent = nfl)
        titans.put()
        texans = Team(title = "Texans", location = "Houston",
                      league = nfl, parent = nfl)
        texans.put()
        
        chiefs = Team(title = "Chiefs", location = "Kansas City",
                      league = nfl, parent = nfl)
        chiefs.put()
        raiders = Team(title = "Raiders", location = "Oakland",
                       league = nfl, parent = nfl)
        raiders.put()
        broncos = Team(title = "Broncos", location = "Denver",
                       league = nfl, parent = nfl)
        broncos.put()
        chargers = Team(title = "Chargers", location = "San Diego",
                        league = nfl, parent = nfl)
        chargers.put()
        
        patriots = Team(title = "Patriots", location = "New England",
                        league = nfl, parent = nfl)
        patriots.put()
        jets = Team(title = "Jets", location = "New York",
                    league = nfl, parent = nfl)
        jets.put()
        dolphins = Team(title = "Dolphins", location = "Miami",
                        league = nfl, parent = nfl)
        dolphins.put()
        bills = Team(title = "Bills", location = "Buffalo",
                     league = nfl, parent = nfl)
        bills.put()
        
        bengals = Team(title = "Bengals", location = "Cincinnati",
                       league = nfl, parent = nfl)
        bengals.put()
        browns = Team(title = "Browns", location = "Cleveland",
                      league = nfl, parent = nfl)
        browns.put()
        steelers = Team(title = "Steelers", location = "Pittsburgh",
                        league = nfl, parent = nfl)
        steelers.put()
        ravens = Team(title = "Ravens", location = "Baltimore",
                      league = nfl, parent = nfl)
        ravens.put()
        
        redskins = Team(title = "Redskins", location = "Washington",
                        league = nfl, parent = nfl)
        redskins.put()
        cowboys = Team(title = "Cowboys", location = "Dallas",
                       league = nfl, parent = nfl)
        cowboys.put()
        giants = Team(title = "Giants", location = "New York",
                      league = nfl, parent = nfl)
        giants.put()
        eagles = Team(title = "Eagles", location = "Philadelphia",
                      league = nfl, parent = nfl)
        eagles.put()

        vikings = Team(title = "Vikings", location = "Minnesota",
                       league = nfl, parent = nfl)
        vikings.put()
        lions = Team(title = "Lions", location = "Detroit",
                     league = nfl, parent = nfl)
        lions.put()
        bears = Team(title = "Bears", location = "Chicago",
                     league = nfl, parent = nfl)
        bears.put()
        packers = Team(title = "Packers", location = "Green Bay",
                       league = nfl, parent = nfl)
        packers.put()
    
        fortyniners = Team(title = "49ers", location = "San Francisco",
                           league = nfl, parent = nfl)
        fortyniners.put()
        seahawks = Team(title = "Seahawks", location = "Seattle",
                        league = nfl, parent = nfl)
        seahawks.put()
        rams = Team(title = "Rams", location = "St. Louis",
                    league = nfl, parent = nfl)
        rams.put()
        cardinals = Team(title = "Cardinals", location = "Arizona",
                         league = nfl, parent = nfl)
        cardinals.put()
        
        saints = Team(title = "Saints", location = "New Orleans",
                      league = nfl, parent = nfl)
        saints.put()
        falcons = Team(title = "Falcons", location = "Atlanta",
                       league = nfl, parent = nfl)
        falcons.put()
        bucs = Team(title = "Buccaneers", location = "Tampa Bay",
                    league = nfl, parent = nfl)
        bucs.put()
        panthers = Team(title = "Panthers", location = "Carolina",
                        league = nfl, parent = nfl)
        panthers.put()
        
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
        

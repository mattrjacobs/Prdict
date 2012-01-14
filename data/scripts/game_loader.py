#!/usr/bin/env python
from datetime import datetime, timedelta, tzinfo
import base64
import cookielib
import iso8601
import optparse
import os
import simplejson as json
import sys
import urllib2

def get_object_by_ref_id(prdict_url, object_type, ref_id):
    get_request = urllib2.Request(url = "%s/api/%ss?q=ref_id:%s" %
                                  (prdict_url, object_type, ref_id),
                                  headers = { "Accept" : "application/json" })
    resp = urllib2.urlopen(get_request)
    return json.loads(resp.read())

def get_object_by_title(prdict_url, object_type, title):
    get_request = urllib2.Request(url = "%s/api/%ss?q=title:%s" %
                                  (prdict_url, object_type, title),
                                  headers = { "Accept" : "application/json" })
    resp = urllib2.urlopen(get_request)
    return json.loads(resp.read())

def get_object_by_uri(prdict_url, uri):
    get_request = urllib2.Request(url = "%s%s" %
                                  (prdict_url, uri),
                                  headers = { "Accept" : "application/json" })
    resp = urllib2.urlopen(get_request)
    return json.loads(resp.read())

def get_teams_by_league(prdict_url, league_uri):
    get_request = urllib2.Request(url = "%s%s/teams" %
                                  (prdict_url, league_uri),
                                  headers = { "Accept" : "application/json" })
    resp = urllib2.urlopen(get_request)
    return json.loads(resp.read())

def get_seasons_by_league(prdict_url, league_uri, season_name):
    get_request = urllib2.Request(url = "%s%s/seasons?q=title:%s" %
                                  (prdict_url, league_uri, season_name),
                                  headers = { "Accept" : "application/json" })
    resp = urllib2.urlopen(get_request)
    return json.loads(resp.read())

def parse_date(date):
    parts = date.strip('Z').split('.')
    dt = datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S")
    return dt.replace(microsecond=int(parts[1]))

def authenticated_http(url, data):
    auth = base64.encodestring('%s:%s' % ("prdictapi.client@gmail.com",
                                          "cbyQ57UyWWWRC768Xshe"))[:-1]
    post_request = urllib2.Request(url = url,
                                   headers = { "Accept" : "application/json",
                                               "Content-Type" : "application/json; charset=utf-8",
                                               "Authorization" : "Basic %s" % auth },
                                   data = json.dumps(data))
    try:
        post_resp = urllib2.urlopen(post_request)
        print "Successful HTTP request"
        return json.loads(post_resp.read())["self"]
    except urllib2.HTTPError, e:
        if e.code == 401:
            print "Unauthorized HTTP Attempt, get the cookie"
            if "Set-Cookie" in e.headers:
                print "Trying again with my new shiny cookie..."
                try:
                    post_resp = urllib2.urlopen(post_request)
                    print "Successful HTTP Request"
                    return json.loads(post_resp.read())["self"]
                except urllib2.HTTPError, e:
                    if e.code == 201:
                        print "Successful HTTP request"
                        status = json.loads(e.read())["status"]
                        if status == "ok":
                            return "ok"
                        else:
                            return None
                    else:
                        print "HTTP Error : %s" % e
                        print "REASON : %s" % e.read()
                        return None
            else:
                print "Did not receive a cookie..."
                return None
        elif e.code == 201:
            print "Successful HTTP request"
            status = json.loads(e.read())["status"]
            if status == "ok":
                return "ok"
            else:
                return None
        else:
            print "HTTP Error : %s" % e
            print "REASON : %s" % e.read()
            return None

def store_league(prdict_url, league_name, league_ref_id):
    current_leagues = get_object_by_ref_id(prdict_url, "league", league_ref_id)["leagues"]["items"]
    if len(current_leagues) > 0:
        print current_leagues
        return current_leagues[0]["self"]
    else:
        print "Need to add the ref ID onto the league"
        leagues_by_name = get_object_by_title(prdict_url, "league", league_name)["leagues"]["items"]
        if len(leagues_by_name) > 0:
            league = leagues_by_name[0]
            update_with_ref_id = { "ref_id" : league_ref_id,
                                   "_method" : "PUT" }
            put_url = "%s%s" % (prdict_url, league["self"])
            put_resp = authenticated_http(put_url, update_with_ref_id)
            if put_resp:
                return put_resp
            else:
                print "Not able to update the league with the ref ID, aborting..."
                sys.exit(1)
        else:
            print "Did not find league of correct name, not adding Ref ID and aborting..."
            sys.exit(1)

def get_season_uri(prdict_url, league_uri, season_name):
    league_seasons_json = get_seasons_by_league(prdict_url, league_uri, season_name)
    seasons_by_title = league_seasons_json["seasons"]["items"]
    if len(seasons_by_title) > 0:
        return seasons_by_title[0]["self"]
    else:
        print "Need to create this season"
        new_season_json = { "title" : season_name,
                            "league" : league_uri }
        post_url = "%s%s/seasons" % (prdict_url, league_uri)
        post_resp = authenticated_http(post_url, new_season_json)
        if post_resp == "ok":
            return get_season_uri(prdict_url, league_uri, season_name)
        else:
            print "Not able to create the season, aborting..."

def load_teams_from_league(league_file):
    print "Using League file : %s" % league_file
    return json.load(open(league_file))

def store_teams(teams, prdict_url, league_uri):
    team_name_uri_map = {}
    team_location_uri_map = {}
    team_ref_id_uri_map = {}
    league_teams = get_teams_by_league(prdict_url, league_uri)
    for api_team in league_teams["teams"]["items"]:
        team_name_uri_map[api_team["title"]] = api_team["self"]
        team_location_uri_map[api_team["location"]] = api_team["self"]
        
    for team in teams:
        current_teams = get_object_by_ref_id(prdict_url, "team", team["id"])["teams"]["items"]
        if len(current_teams) > 0:
            print "Found Ref ID for %s at : %s" % (team["name"], current_teams[0]["self"])
            team_ref_id_uri_map[team["id"]] = current_teams[0]["self"]
        else:
            print "Did not find Ref ID for %s, adding it..." % team["name"]
            team_name = team["name"].split()[-1:][0]
            alternate_team_name = " ".join(team["name"].split()[-2:])
            team_location = team["name"].split()[:1][0]
            alternate_team_location = " ".join(team["name"].split()[:2])
            team_uri = None
            if team_name in team_name_uri_map:
                team_uri = team_name_uri_map[team_name]
            elif alternate_team_name in team_name_uri_map.keys():
                team_uri = team_name_uri_map[alternate_team_name]
            else:
                if team_location in team_location_uri_map:
                    team_uri = team_location_uri_map[team_location]
                elif alternate_team_location in team_location_uri_map:
                    team_uri = team_location_uri_map[alternate_team_location]
                else:
                    print "Could not find URI for team : %s" % team["name"]
                    sys.exit(1)

            api_team = get_object_by_uri(prdict_url, team_uri)
            update_with_ref_id = { "ref_id" : team["id"],
                                   "_method" : "PUT" }
            put_url = "%s%s" % (prdict_url, api_team["self"])
            put_resp = authenticated_http(put_url, update_with_ref_id)
            if not put_resp:
                print "Not able to update the team with the ref ID, aborting..."
                sys.exit(1)
            else:
                team_ref_id_uri_map[team["id"]] = put_resp
    return team_ref_id_uri_map

def download_team_schedules(teams, prdict_url, team_dir):
    fanfeedr_base = "http://ffapi.fanfeedr.com/basic/api"
    api_key = "hqxv2tyfmmhu68zfn9nfsfsv"
    file_map = {}

    for team in teams:
        print "Retrieving games for %s...(%s)" % (team["name"], team["id"])
        team_ref_id = team["id"]
        filename = "%s/%s.json" % (team_dir, team_ref_id)
        try:
            game = json.load(open(filename))
            print "File already exists"
            file_map[team["id"]] = filename
        except IOError:
            print "File not already present"
            url = "%s/teams/%s/events?api_key=%s" % \
                  (fanfeedr_base, team["id"], api_key)
            try:
                response = urllib2.urlopen(url)
                games_json = response.read()
                f = open(filename, 'w')
                f.write(games_json)
                f.close()
                file_map[team["id"]] = filename
            except urllib2.HTTPError:
                print "HTTP ERROR retrieving schedule from Fanfeedr"
    return file_map

def store_games(team_map, league_uri, season_uri, prdict_url):

    class EstTzInfo(tzinfo):
        def utcoffset(self, dt): return timedelta(hours=-4)
        def dst(self, dt): return timedelta(0)
        def tzname(self, dt): return 'EST+04EDT'
        def olsen_name(self): return 'US/Eastern'

    class UstTzInfo(tzinfo):
        def utcoffset(self, dt): return timedelta(hours=0)
        def dst(self, dt): return timedelta(0)
        def tzname(self, dt): return 'UST'
        def olsen_name(self): return 'UST' 

    # Key: Team name, Value (#already there, #added)
    games_stored = {}

    for k in team_map:
        num_added = 0
        num_found = 0
        (uri, fanfeedr_name, schedule_file) = team_map[k]
        print "Now working on team : %s" % fanfeedr_name
        
        json_schedule = json.load(open(schedule_file))
        for json_game in json_schedule:
            date = json_game["date"]
            name = json_game["name"]
            game_ref_id = json_game["id"]
            name_pieces = map(lambda x: x.strip(), name.split("@"))
            away_name = name_pieces[0]
            home_name = name_pieces[1]
                    
            json_event = get_object_by_ref_id(prdict_url, "event", game_ref_id)["events"]["items"]
            if len(json_event) == 0:
                print "Did not find event : %s, creating it..." % game_ref_id
                home_team_uri = _get_uri_by_team(team_map, home_name)
                away_team_uri = _get_uri_by_team(team_map, away_name)
                parsed_date = parse_date(date).replace(tzinfo = EstTzInfo()).astimezone(UstTzInfo())
                end_date = timedelta(hours=4) + parsed_date
                completed = end_date < datetime.utcnow().replace(tzinfo = UstTzInfo())
                start_date_str = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
                new_event = { "type" : "sportsevent",
                              "title" : name,
                              "home_team" : home_team_uri,
                              "away_team" : away_team_uri,
                              "league" : league_uri,
                              "season" : season_uri,
                              "completed" : 'false',
                              "cancelled" : 'false',
                              "game_kind" : "Regular Season",
                              "ref_id" : game_ref_id,
                              "start_date" : start_date_str,
                              "end_date" : end_date_str }
                post_url = "%s/api/events" % prdict_url
                post_resp = authenticated_http(post_url, new_event)
                if not post_resp:
                    print "Not able to create the event, aborting..."
                    sys.exit(1)
                else:
                    num_added = num_added + 1
            else:
                print "Found event : %s" % game_ref_id
                num_found = num_found + 1
        games_stored[fanfeedr_name] = (num_found, num_added)

    return games_stored

def _get_uri_by_team(m, name):
    for (_, (uri, fanfeedr_name, _)) in m.iteritems():
        if name == fanfeedr_name:
            return uri

    print "Could not look up Fanfeedr name : %s" % name
    sys.exit(1)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-l', action="store", dest="league_file")
    parser.add_option('-t', action="store", dest="team_dir")
    parser.add_option('-p', action="store", dest="prdict_url")
    parser.add_option('-n', action="store", dest="league_name")
    parser.add_option('-r', action="store", dest="league_ref_id")
    parser.add_option('-s', action="store", dest="season_name")
    (options, args) = parser.parse_args()
    if not options.league_file:
        print "League file is required"
        sys.exit(1)
    if not options.team_dir:
        print "Team dir is required"
        sys.exit(1)
    if options.team_dir.endswith("/"):
        print "No trailing slash for team dir"
        sys.exit(1)
    if not options.prdict_url:
        print "Prdict URL is required"
        sys.exit(1)
    if options.prdict_url.endswith("/"):
        print "No trailing slash for prdict URL"
        sys.exit(1)
    if not options.league_name:
        print "League name is required"
        sys.exit(1)
    if not options.season_name:
        print "Season name is required"
        sys.exit(1)
    if not options.league_ref_id:
        print "League Ref ID is required"
        sys.exit(1)

    cookiejar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(opener)

    print "Starting up..."
    league_uri = store_league(options.prdict_url, options.league_name, options.league_ref_id)
    print "League URI : %s" % league_uri

    season_uri = get_season_uri(options.prdict_url, league_uri, options.season_name)
    print "Season URI : %s" % season_uri

    teams = load_teams_from_league(options.league_file)
    print "Found %d teams" % len(teams)

    #This map goes from Fanfeedr ref_id to Prdict URI
    team_uri_map = store_teams(teams, options.prdict_url, league_uri)

    team_map = {}
    for k in team_uri_map.keys():
        uri = team_uri_map[k]
        fanfeedr_name = filter(lambda team: team["id"] == k, teams)[0]["name"]
        team_map[k] = (uri, fanfeedr_name)
        
    file_list_map = download_team_schedules(teams, options.prdict_url, options.team_dir)
    for k in team_map.keys():
        (uri, fanfeedr_name) = team_map[k]
        schedule_file = file_list_map[k]
        team_map[k] = (uri, fanfeedr_name, schedule_file)

    for k in team_map.keys():
        (uri, fanfeedr_name, schedule_file) = team_map[k]
        print "%s : %s : %s : %s" % (fanfeedr_name, uri, k, schedule_file)

    games_stored = store_games(team_map, league_uri, season_uri, options.prdict_url)
    for k in games_stored:
        (found, added) = games_stored[k]
        print "%s : Found : %d, Added : %d" % (k, found, added)

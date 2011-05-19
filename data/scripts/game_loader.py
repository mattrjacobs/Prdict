#!/usr/bin/env python
import simplejson as json

def load_games():

    json_data = None
    for line in open("../raw/mlb_events.json"):
        json_data = line

    num = 0
    for json_game in json.loads(json_data):
        #home_team = json_game["away"]["team"]["title"]
        #away_team = json_game["home"]["team"]["title"]
        name_str = json_game["name"]
        date_str = json_game["date"]
        woo_str = "%s %s" % (date_str, name_str)
        print woo_str
        num = num + 1
    print "NUM : %d" % num

if __name__ == "__main__":
    load_games()

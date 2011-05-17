#!/usr/bin/env python
import simplejson as json

def load_games():

    json_data = None
    for line in open("../parsed/mlb_2011.json"):
        json_data = line

    for json_game in json.loads(json_data):
        home_team = json_game["away"]["team"]["title"]
        away_team = json_game["home"]["team"]["title"]
        date_str = json_game["date"]["rfc822"]
        woo_str = "%s %s %s" % (date_str, home_team, away_team)
        print woo_str

if __name__ == "__main__":
    load_games()

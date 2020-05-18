import requests
import pickle
import yaml
import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute(
    '''CREATE TABLE entries
        (summonerId text, summonerName text, leaguePoints text, rank text, wins text, losses text, veteran text,
        inactive text, freshBlood text, hotStreak text)'''
)


with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)

API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5",
                 headers=REQUEST_HEADERS)

entries = r.json()["entries"]
for entry in entries:
    summoner_id = entry["summonerId"]
    summoner_name = entry["summonerName"]
    league_points = entry["leaguePoints"]
    rank = entry["rank"]
    wins = entry["wins"]
    losses = entry["losses"]
    veteran = entry["veteran"]
    inactive = entry["inactive"]
    fresh_blood = entry["freshBlood"]
    hot_streak = entry["hotStreak"]
    insert = (summoner_id, summoner_name, league_points, rank, wins, losses, veteran, inactive, fresh_blood, hot_streak)
    c.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)', insert)
    conn.commit()

conn.close()

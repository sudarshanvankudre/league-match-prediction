import requests
import sqlite3
import yaml
import time

# data model : (summonerId text, summonerName text, leaguePoints text, rank text, wins text, losses text, veteran text,
#         inactive text, freshBlood text, hotStreak text)

with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)
API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

conn = sqlite3.connect('data.db')
c = conn.cursor()
try:
    c.execute(
        '''CREATE TABLE summoners
            (accountId text, profileIconId text, revisionDate text, name text, id text, puuid text, summonerLevel text)'''
    )
except sqlite3.OperationalError:
    pass

entries = [row for row in c.execute('SELECT * FROM entries')]
count = 0
while len(entries) > 0:
    entry = entries.pop()
    summoner_id = entry[0]
    summoner_request = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summoner_id, headers=REQUEST_HEADERS)
    if summoner_request.status_code == 429:
        print("Total summoners processed: {}".format(count))
        wait_time = int(summoner_request.headers["Retry-After"])
        entries.append(entry)
        minutes, seconds = divmod(wait_time, 60)
        print("Waiting for {} minutes {} seconds...".format(minutes, seconds))
        time.sleep(wait_time)
    else:
        count += 1
        summoner = summoner_request.json()
        account_id = summoner["accountId"]
        profile_icon_id = summoner["profileIconId"]
        revision_date = summoner["revisionDate"]
        name = summoner["name"]
        id = summoner["id"]
        puuid = summoner["puuid"]
        summoner_level = summoner["summonerLevel"]
        insert = (account_id, profile_icon_id, revision_date, name, id, puuid, summoner_level)
        c.execute('INSERT INTO summoners VALUES (?, ?, ?, ?, ?, ?, ?)', insert)
        conn.commit()
print(count)
conn.close()
import requests
import yaml
import pymongo
import time

with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)
API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

db = pymongo.MongoClient().riot_data
matches = db.matches.find({})
leftover = []

count = 0
for match_entry in matches:
    matchid = match_entry["gameId"]
    r = requests.get(API_URL + "/lol/match/v4/matches/" + str(matchid), headers=REQUEST_HEADERS)
    if r.status_code == 429:
        print("Total matches processed: {}".format(count))
        leftover.append(matchid)
        wait_time = int(r.headers["Retry-After"])
        minutes, seconds = divmod(wait_time, 60)
        print("Waiting for {} minutes {} seconds...".format(minutes, seconds))
        time.sleep(wait_time)
    elif r.status_code == 200:
        db.games.insert_one(r.json())
        count += 1

while len(leftover) > 0:
    matchid = leftover.pop()
    r = requests.get(API_URL + "/lol/match/v4/matches/" + str(matchid), headers=REQUEST_HEADERS)
    if r.status_code == 429:
        print("Total matches processed: {}".format(count))
        leftover.append(matchid)
        wait_time = int(r.headers["Retry-After"])
        minutes, seconds = divmod(wait_time, 60)
        print("Waiting for {} minutes {} seconds...".format(minutes, seconds))
        time.sleep(wait_time)
    elif r.status_code == 200:
        print("Processing...")
        db.games.insert_one(r.json())
        count += 1
print(count)



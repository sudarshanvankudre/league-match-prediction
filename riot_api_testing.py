import requests
import json
import time
import yaml
import pickle

with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)

API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

# First get all of the league entries for challenger

# We will be focusing solely on ranked solo 5v5 queue
r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5",
                 headers=REQUEST_HEADERS)
data = r.json()
entries = data["entries"]
count = 0
while len(entries) > 0:
    entry = entries.pop()
    summonerid = entry["summonerId"]
    summoner_request = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summonerid, headers=REQUEST_HEADERS)
    if summoner_request.status_code == 429:
        print("Total summoners processed: {}".format(count))
        wait_time = int(summoner_request.headers["Retry-After"])
        entries.append(entry)
        print("Waiting for {} minutes...".format(wait_time / 60))
        time.sleep(wait_time)
    else:
        count += 1
        summoner = summoner_request.json()
        with open("input/summoners.txt", "wb") as summoners_dump:
            pickle.dump(summoner, summoners_dump)

print(count)

# For each summoner, get a list of matches using the encrypted account id




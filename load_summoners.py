import requests
import yaml
import time
import pymongo

with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)
API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

db = pymongo.MongoClient().riot_data

entries = list(db.entries.find({}))
count = 0
while len(entries) > 0:
    entry = entries.pop()
    summoner_id = entry["summonerId"]
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
        db.summoners.insert_one(summoner)
print(count)

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
summoners = list(db.summoners.find({}))

count = 0
game_ids = set()
while len(summoners) > 0:
    summoner = summoners.pop()
    account_id = summoner["accountId"]
    match_request = requests.get(API_URL + "/lol/match/v4/matchlists/by-account/" + account_id, headers=REQUEST_HEADERS)
    if match_request.status_code == 429:
        print("Total summoners processed: {}".format(count))
        wait_time = int(match_request.headers["Retry-After"])
        summoners.append(summoner)
        minutes, seconds = divmod(wait_time, 60)
        print("Waiting for {} minutes {} seconds...".format(minutes, seconds))
        time.sleep(wait_time)
    else:
        match_data = match_request.json()
        try:
            for match in match_data["matches"]:
                if match["gameId"] not in game_ids:
                    db.matches.insert_one(match)
                    game_ids.add(match["gameId"])
        except KeyError:
            print("This doesn't have matches:\n {}".format(match_data))
            print("Status code: {}".format(match_request.status_code))
        count += 1
print(count)

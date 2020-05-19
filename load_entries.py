import requests
import yaml
import pymongo

db = pymongo.MongoClient().riot_data

with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)

API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5",
                 headers=REQUEST_HEADERS)

entries = r.json()["entries"]
result = db.entries.insert_many(entries)

import requests
import pickle
import yaml

with open("config.yml", 'r') as config:
    config_data = yaml.safe_load(config)

API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]

r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5",
                 headers=REQUEST_HEADERS)

entries = r.json()["entries"]
with open("input/entries.txt", 'wb') as entry_dump:
    pickle.dump(entries, entry_dump)

with open("input/entries.txt", 'rb') as entry_dump:
    loaded_entries = pickle.load(entry_dump)
assert entries == loaded_entries

import pymongo
import json

db = pymongo.MongoClient().datastore
docs = list(db.games.find({"gameMode": "CLASSIC"}))
with open('games.json', 'w') as games_file:
    for d in docs:
        json.dump(d, games_file)

docs = list(db.summoner_winrates.find())
winrates = {d["accountId"]: d["winrate"] for d in docs}
with open('winrates.json', 'w') as winrates_file:
    json.dump(winrates, winrates_file)


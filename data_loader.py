import requests
from google.cloud import firestore
import yaml
import pymongo
import time

with open('config.yml', 'r') as config:
    config_data = yaml.safe_load(config)
    database = config_data["database"]

if database == "firestore":
    db = firestore.Client()
elif database == "mongodb":
    db = pymongo.MongoClient().datastore

API_URL = config_data["request_info"]["API_URL"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]


def load_into(db_name, doc, collection_name):
    """Writes doc to db.collection corresponding to db_name"""
    print(db_name)
    if db_name == "firestore":
        db.collection(collection_name).document().set(doc)
    elif db_name == "mongodb":
        eval_string = "db.{}.insert_one(doc)".format(collection_name)
        eval(eval_string)


def load_many(db_name, docs, collection_name):
    """Writes all docs in docs to db.collection corresponding to db_name"""
    print(db_name)
    if db_name == "firestore":
        batch = db.batch()
        for doc in docs:
            ref = db.collection(collection_name).document()
            batch.set(ref, doc)
        batch.commit()
    elif db_name == "mongodb":
        eval_string = "db.{}.insert_many(docs)".format(collection_name)
        eval(eval_string)


def validate_response(r):
    if r.status_code != 200 and r.status_code != 429:
        print("Response status code is {}!".format(r.status_code))
        print("Response: \n", r)
        return


def handle_rate_limit(r, count):
    try:
        print("Total responses processed: {}".format(count))
        wait_time = int(r.headers["Retry-After"])
        minutes, seconds = divmod(wait_time, 60)
        print("Waiting for {} minutes {} seconds...".format(minutes, seconds))
        time.sleep(wait_time)
    except Exception as e:
        print("Exception thrown: ", e)
        print("Response: ", r)
        pass


def get_response(api, *args):
    print(api)
    print(args)
    print(type(args))


def get_collection(db_name, collection_name):
    """Returns an iterable of documents from the collection_name in db corresponding to db_name"""
    if db_name == "firestore":
        return db.collection(collection_name).stream()
    elif db_name == "mongodb":
        eval_string = "db.{}.find({})".format(collection_name, "")
        return eval(eval_string)


def load_challenger_entries(queue='RANKED_SOLO_5x5'):
    """Loads all of the entries from riot into database"""
    r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/" + queue, headers=REQUEST_HEADERS)
    validate_response(r)
    try:
        entries = r.json()["entries"]
        load_many(database, entries, "challenger_entries")
    except KeyError:
        print("Response doesn't have 'entries' key!")


def load_challenger_summoners():
    """Loads all of the summoners from riot api depending on the existing league entries in db"""
    entries = list(get_collection(database, "challenger_entries"))
    print(len(entries))
    count = 0
    while len(entries) > 0:
        entry = entries.pop()
        e = entry.to_dict()
        summoner_id = e["summonerId"]
        r = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summoner_id, headers=REQUEST_HEADERS)
        validate_response(r)
        if r.status_code == 429:
            entries.append(entry)
            handle_rate_limit(r, count)
        else:
            count += 1
            print("Adding summoners to database...")
            load_into(database, r.json(), "challenger_summoners")
    print("{} summoners loaded".format(count))


def load_challenger_games():
    summoners = list(get_collection(database, "challenger_summoners"))
    game_count = 0
    seen_games = set()
    while len(summoners) > 0:
        summoner = summoners.pop()
        s = summoner.to_dict()
        account_id = s["accountId"]
        match_response = requests.get(API_URL + "/lol/match/v4/matchlists/by-account/" + account_id,
                                      headers=REQUEST_HEADERS)
        validate_response(match_response)
        if match_response.status_code == 429:
            summoners.append(summoner)
            handle_rate_limit(match_response, -1)
        else:
            matches = match_response.json()["matches"]
            leftover_games = []
            for match in matches:
                match_id = match["gameId"]
                if match_id not in seen_games:
                    game_response = requests.get(API_URL + "/lol/match/v4/matches/" + str(match_id), headers=REQUEST_HEADERS)
                    validate_response(game_response)
                    if game_response.status_code == 429:
                        leftover_games.append(game_response)
                        handle_rate_limit(game_response, game_count)
                    else:
                        game_count += 1
                        seen_games.add(match_id)
                        load_into(database, game_response.json(), "challenger_games")

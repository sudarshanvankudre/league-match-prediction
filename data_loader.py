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
    count = 0
    while len(entries) > 0:
        entry = entries.pop()
        e = entry.to_dict()
        summoner_id = e["summonerId"]
        r = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summoner_id, headers=REQUEST_HEADERS)
        validate_response(r)
        if r.status_code == 429:
            print("Total summoners processed: {}".format(count))
            wait_time = int(r.headers["Retry-After"])
            entries.append(entry)
            minutes, seconds = divmod(wait_time, 60)
            print("Waiting for {} minutes {} seconds...".format(minutes, seconds))
            time.sleep(wait_time)
        else:
            count += 1
            print("Adding summoners to database...")
            load_into(database, e, "challenger_summoners")
    print("{} summoners loaded".format(count))
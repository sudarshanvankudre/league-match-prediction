import requests
from google.cloud import firestore
import yaml
import pymongo

with open('config.yml', 'r') as config:
    config_data = yaml.safe_load(config)
    database = config_data["database"]

if database == "firestore":
    db = firestore.Client()
elif database == "mongodb":
    db = pymongo.MongoClient().datastore

API_URL = config_data["request_info"]["API_URL"]
API_KEY = config_data["request_info"]["API_KEY"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]


def load_into(db_name, doc, collection_name):
    """Writes doc to db.collection corresponding to db_name"""
    if db_name == "firestore":
        db.collection(collection_name).document().set(doc)
    elif db_name == "mongodb":
        eval_string = "db.{}.insert_one(doc)".format(collection_name)
        eval(eval_string)


def load_many(db_name, docs, collection_name):
    """Writes all docs in docs to db.collection corresponding to db_name"""
    if db_name == "firestore":
        batch = db.batch()
        for doc in docs:
            ref = db.collection(collection_name).document()
            batch.update(ref, doc)
    elif db_name == "mongodb":
        eval_string = "db.{}.insert_many(docs)".format(collection_name)
        eval(eval_string)


def get_collection(db_name, collection_name):
    """Returns an iterable of documents from the collection_name in db corresponding to db_name"""
    if db_name == "firestore":
        return db.collection(collection_name).stream()
    elif db_name == "mongodb":
        eval_string = "db.{}.find({})".format(collection_name, "")
        return eval(eval_string)


class ChallengerEntriesLoader():
    """Object for loading all the challenger league entries from riot api directly into database.
    Drops existing collection if it exists. 
    """
    def __init__(self, queue='RANKED_SOLO_5X5'):
        self.queue = queue

    def load(self):
        """Loads all of the entries from riot into database"""
        r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/" + self.queue, headers=REQUEST_HEADERS)
        assert r.status_code == 200, "Response status code is {}!".format(r.status_code)
        try:
            entries = r.json()["entries"]
            load_many("firestore", entries, "challenger_entries")
        except KeyError:
            print("Response doesn't have 'entries' key!")


class ChallengerSummonersLoader:
    """Object for loading all challenger summoners from riot api, assuming that entries already exist in db"""

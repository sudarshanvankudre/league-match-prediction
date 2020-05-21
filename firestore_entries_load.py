from google.cloud import firestore
import pymongo

db = firestore.Client()

mongodb = pymongo.MongoClient().riot_data


for match in mongodb.matches.find({}):
    del match["_id"]
    db.collection("challenger-matches").document().set(match)
    break

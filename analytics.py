from google.cloud import firestore

db = firestore.Client()


def count(collection_name):
    """Returns the number of documents currently in the given collection"""
    docs = db.collection(collection_name).stream()
    return sum(1 for _ in docs)


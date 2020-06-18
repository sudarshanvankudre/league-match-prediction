import itertools
import time

import pymongo
import requests
import yaml
from google.cloud import firestore
from requests.exceptions import ConnectionError

apis = {
    "CHALLENGER_LEAGUE_ENTRIES": "/lol/league/v4/challengerleagues/by-queue/",
    "SUMMONER": "/lol/summoner/v4/summoners/"
}

with open('leaguepredict/match_prediction/config.yml', 'r') as config:
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
    if db_name == "firestore":
        db.collection(collection_name).document().set(doc)
    elif db_name == "mongodb":
        eval_string = "db.{}.insert_one(doc)".format(collection_name)
        eval(eval_string)


def load_many(db_name, docs, collection_name):
    """Writes all docs in docs to db.collection corresponding to db_name and collection corresponding to
    collection_name"""
    if db_name == "firestore":
        batch = db.batch()
        for doc in docs:
            ref = db.collection(collection_name).document()
            batch.set(ref, doc)
        batch.commit()
    elif db_name == "mongodb":
        try:
            eval_string = "db.{}.insert_many(docs)".format(collection_name)
            eval(eval_string)
        except Exception as e:
            print(e)


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
    """Gets http response and makes sure that the response is valid. If not, does the appropriate actions."""
    # todo: finish this method
    # api is the main
    request = (API_URL + apis[api]).join(args)


def get_collection(db_name, collection_name):
    """Returns an iterable of documents from the collection_name in db corresponding to db_name"""
    if db_name == "firestore":
        docs = db.collection(collection_name).stream()
        return (d.to_dict() for d in docs)
    elif db_name == "mongodb":
        eval_string = "db.{}.find({})".format(collection_name, "")
        return eval(eval_string)


def load_entries(tier, division=None, queue='RANKED_SOLO_5x5'):
    """Loads all of the challenger entries from riot into database
    Possible tiers are challenger, grandmaster, master, diamond, platinum, gold, silver, bronze, and iron"""
    tier_request = {
        ("challenger", division): "/lol/league/v4/challengerleagues/by-queue/",
        ("grandmaster", division): "/lol/league/v4/grandmasterleagues/by-queue/",
        ("master", division): "/lol/league/v4/masterleagues/by-queue/",
        ("diamond", division): "/lol/league/v4/entries/{}/{}/{}".format(queue, tier.upper(), division)
    }
    if tier == "diamond":
        infinite = itertools.count(1)
        leftover = []
        while True:
            page = next(infinite)
            print("Page: ", page)
            try:
                r = requests.get(API_URL + tier_request[(tier, division)] + "?page={}".format(page),
                             headers=REQUEST_HEADERS)
            except ConnectionError:
                infinite = itertools.count(page)
                continue
            validate_response(r)
            if r.status_code == 429:
                leftover.append(r)
                handle_rate_limit(r, -1)
            try:
                response = r.json()
                if len(response) == 0 or page > 5:
                    break
                load_many(database, response, "entries")
            except Exception as e:
                print(e)
                break
        while len(leftover) > 0:
            r = leftover.pop()
            response = r.json()
            load_many(database, response, "entries")
    else:
        try:
            r = requests.get(API_URL + tier_request[(tier, division)] + queue, headers=REQUEST_HEADERS)
            validate_response(r)
        except ConnectionError:
            time.sleep(10)
            load_entries(tier, division)
        try:
            entries = r.json()["entries"]
            load_many(database, entries, "entries")
        except KeyError:
            print("Response doesn't have 'entries' key!")


@DeprecationWarning
def load_challenger_entries(queue='RANKED_SOLO_5x5'):
    """Loads all of the challenger entries from riot into database"""
    r = requests.get(API_URL + "/lol/league/v4/challengerleagues/by-queue/" + queue, headers=REQUEST_HEADERS)
    validate_response(r)
    try:
        entries = r.json()["entries"]
        load_many(database, entries, "challenger_entries")
    except KeyError:
        print("Response doesn't have 'entries' key!")


@DeprecationWarning
def load_grandmaster_entries(queue='RANKED_SOLO_5x5'):
    """Loads all of the grandmaster entries from riot into database"""
    r = requests.get(API_URL + "/lol/league/v4/grandmasterleagues/by-queue/" + queue, headers=REQUEST_HEADERS)
    validate_response(r)
    try:
        entries = r.json()["entries"]
        load_many(database, entries, "grandmaster_entries")
    except KeyError:
        print("Response doesn't have 'entries' key!")


def load_summoners():
    """Loads all summoners from riot api depending on existing league entries in db"""
    entries = list(get_collection(database, "entries"))
    print(len(entries))
    count = 0
    while len(entries) > 0:
        e = entries.pop()
        summoner_id = e["summonerId"]
        try:
            r = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summoner_id, headers=REQUEST_HEADERS)
        except ConnectionError:
            entries.append(e)
            continue
        validate_response(r)
        if r.status_code == 429:
            entries.append(e)
            handle_rate_limit(r, count)
        else:
            count += 1
            print("Adding summoners to database...")
            load_into(database, r.json(), "summoners")
    print("{} summoners loaded".format(count))


@DeprecationWarning
def load_challenger_summoners():
    """Loads all of the challenger summoners from riot api depending on the existing league entries in db"""
    entries = list(get_collection(database, "challenger_entries"))
    print(len(entries))
    count = 0
    while len(entries) > 0:
        e = entries.pop()
        summoner_id = e["summonerId"]
        r = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summoner_id, headers=REQUEST_HEADERS)
        validate_response(r)
        if r.status_code == 429:
            entries.append(e)
            handle_rate_limit(r, count)
        else:
            count += 1
            print("Adding summoners to database...")
            load_into(database, r.json(), "challenger_summoners")
    print("{} summoners loaded".format(count))


@DeprecationWarning
def load_grandmaster_summoners():
    """Loads all of the grandmaster summoners from riot api depending on the existing league entries in db"""
    entries = list(get_collection(database, "challenger_entries"))
    print(len(entries))
    count = 0
    while len(entries) > 0:
        e = entries.pop()
        summoner_id = e["summonerId"]
        r = requests.get(API_URL + "/lol/summoner/v4/summoners/" + summoner_id, headers=REQUEST_HEADERS)
        validate_response(r)
        if r.status_code == 429:
            entries.append(e)
            handle_rate_limit(r, count)
        else:
            count += 1
            print("Adding summoners to database...")
            load_into(database, r.json(), "challenger_summoners")
    print("{} summoners loaded".format(count))


def load_games():
    """Loads all games from riot api based on current summoners in db."""
    summoners = list(get_collection(database, "summoners"))
    game_count = 0
    seen_games = set()
    while len(summoners) > 0:
        s = summoners.pop()
        try:
            account_id = s["accountId"]
        except KeyError:
            print("accountId not in summoner data")
            continue
        try:
            match_response = requests.get(API_URL + "/lol/match/v4/matchlists/by-account/" + account_id,
                                      headers=REQUEST_HEADERS)
        except ConnectionError:
            summoners.append(s)
            continue
        validate_response(match_response)
        if match_response.status_code == 429:
            summoners.append(s)
            handle_rate_limit(match_response, -1)
        else:
            try:
                matches = match_response.json()["matches"]
            except Exception as e:
                print("Exception was: ", e)
                continue
            leftover_games = []
            i = 0
            while i < len(matches):
                match_id = matches[i]["gameId"]
                if match_id not in seen_games:
                    try:
                        game_response = requests.get(API_URL + "/lol/match/v4/matches/" + str(match_id),
                                                 headers=REQUEST_HEADERS)
                    except ConnectionError:
                        continue
                    validate_response(game_response)
                    if game_response.status_code == 429:
                        leftover_games.append(game_response)
                        handle_rate_limit(game_response, game_count)
                    else:
                        game_count += 1
                        seen_games.add(match_id)
                        load_into(database, game_response.json(), "games")
                i += 1


@DeprecationWarning
def load_challenger_games():
    summoners = list(get_collection(database, "challenger_summoners"))
    game_count = 0
    seen_games = set()
    while len(summoners) > 0:
        s = summoners.pop()
        try:
            account_id = s["accountId"]
        except KeyError:
            print("accountId not in summoner data")
            continue
        match_response = requests.get(API_URL + "/lol/match/v4/matchlists/by-account/" + account_id,
                                      headers=REQUEST_HEADERS)
        validate_response(match_response)
        if match_response.status_code == 429:
            summoners.append(s)
            handle_rate_limit(match_response, -1)
        else:
            try:
                matches = match_response.json()["matches"]
            except Exception as e:
                print("Exception was: ", e)
                continue
            leftover_games = []
            for match in matches:
                match_id = match["gameId"]
                if match_id not in seen_games:
                    game_response = requests.get(API_URL + "/lol/match/v4/matches/" + str(match_id),
                                                 headers=REQUEST_HEADERS)
                    validate_response(game_response)
                    if game_response.status_code == 429:
                        leftover_games.append(game_response)
                        handle_rate_limit(game_response, game_count)
                    else:
                        game_count += 1
                        seen_games.add(match_id)
                        load_into(database, game_response.json(), "challenger_games")

import pymongo
from data_loader import load_into

db = pymongo.MongoClient().datastore


def load_winrates(summoner_collection_name, games_collection_name, mode="CLASSIC"):
    """Adds a winrate collection to db that has all of the winrates for each summoner in the summoner_collection_name
    collection using the data from the games_collection_name collection.
    """

    def is_valid_game(game, account_id):
        try:
            if game["gameMode"] != mode:
                return False
            participating = False
            for p in game["participantIdentities"]:
                if p["player"]["accountId"] == account_id:
                    participating = True
            return participating
        except KeyError as e:
            print(e)

    # iterate over all summoners in db and calculate winrate for each one. This is a very expensive operation.
    summoner_collection = eval("db.{}".format(summoner_collection_name))
    summoners = summoner_collection.find({})
    for summoner in summoners:
        games_collection = eval("db.{}".format(games_collection_name))
        games = games_collection.find({})
        account_id = summoner["accountId"]
        wins = 0
        total = 0
        for game in games:
            if is_valid_game(game, account_id):
                total += 1
                for p in game["participantIdentities"]:
                    if p["player"]["accountId"] == account_id:
                        participant_id = p["participantId"]
                win = False
                for p in game["participants"]:
                    if p["participantId"] == participant_id and p["stats"]["win"]:
                        win = True
                        break
                if win:
                    wins += 1

        try:
            winrate = wins / total
        except ZeroDivisionError:
            winrate = 0
        doc = {"accountId": account_id, "winrate": winrate}
        load_into("mongodb", doc, "summoner_winrates")

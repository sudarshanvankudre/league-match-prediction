import pymongo

db = pymongo.MongoClient().datastore



def load_winrates(summoner_collection_name, games_collection_name, mode="CLASSIC"):
    """Adds a winrate collection to db that has all of the winrates for each summoner in the summoner_collection_name
    collection using the data from the games_collection_name collection.
    """
    def game_check(game):
        if game["gameMode"] != mode:
            return False
        participating = False
        for p in game["participantIdentities"]:
            if p["player"]["accountId"] == account_id:
                participating = True
        return participating
    # iterate over all summoners in db and calculate winrate for each one. This is a very expensive operation.
    summoner_collection = eval("db.{}".format(summoner_collection_name))
    summoners = summoner_collection.find({})
    try:
        for summoner in summoners:
            games_collection = eval("db.{}".format(games_collection_name))
            games = games_collection.find({})
            account_id = summoner["accountId"]
            wins = 0
            total = 0
            for game in filter(game_check, games):
                total += 1

    except Exception as e:
        print(e)



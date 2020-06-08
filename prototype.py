"""This is a prototype that displays different attributes of the feature vectors that have been obtained from the riot api. These features are
displayed as a distribution.
"""
import pymongo
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Perceptron
AVG_WINRATE = 0.5144688460788702

# input vector construction: [topchamp1, midchamp1, jngchamp1, botchamp1, suppchamp1, topchamp2, midchamp2, jngchamp2,
# botchamp2, suppchamp2, winrates for team1 in same order, winrates for team2 in same order]
# input vector: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, corresponding winrates]



team = 0

attributes = ["baronKills", "dragonKills", "inhibitorKills", "riftHeraldKills", "towerKills"]
# attribute = attributes[np.random.randint(0, len(attributes))]
attribute = "towerKills"
# first, we have to get the data from the mongodb store that's on summoner's rift (map id 11)
db = pymongo.MongoClient().datastore
docs = db.challenger_games.find({"gameMode":"CLASSIC"})
games = []
seen = set()
for d in docs:
    try:
        if d["gameId"] not in seen:
            if d["mapId"] == 11:
                games.append(d)
            seen.add(d["gameId"])
    except KeyError:
        print("key error")

print("Getting data...")
X = []
y = []
for g in games:
    winrates = []
    vector = []
    for p in g["participants"]:
        champion_id = p["championId"]
        vector.append(champion_id)
        account_id = g["participantIdentities"][p["participantId"] - 1]["player"]["accountId"]
        temp = db.summoner_winrates.find({"accountId": account_id})
        try:
            doc = next(temp)
            winrate = doc["winrate"]
        except StopIteration:
            winrate = AVG_WINRATE
        winrates.append(winrate)
    vector.extend(winrates)
    X.append(vector)
    team1 = g["teams"][0]
    if team1["teamId"] == 100 and team1["win"] == "Win":
        y.append(1)
    elif team1["teamId"] == 100:
        y.append(0)
    elif team1["teamId"] == 200 and team1["win"] == "Win":
        y.append(0)
    else:
        y.append(1)

print("Training on data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
clf = Perceptron(random_state=42)
clf.fit(X_train, y_train)
print("test accuracy of: ", clf.score(X_test, y_test))


# data = [g["teams"][team][attribute] for g in train]

# plt.hist(data)
# plt.show()
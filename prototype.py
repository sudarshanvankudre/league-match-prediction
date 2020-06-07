"""This is a prototype that displays different attributes of the feature vectors that have been obtained from the riot api. These features are
displayed as a distribution.
"""
import pymongo
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Perceptron

# input vector construction: [topchamp1, midchamp1, jngchamp1, botchamp1, suppchamp1, topchamp2, midchamp2, jngchamp2,
# botchamp2, suppchamp2, winrates for team1 in same order, winrates for team2 in same order]



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

X = [[g["teams"][team][a] for a in attributes] for g in games]
# wins are 1, fails are 0
y = [1 if g["teams"][team]["win"] == "Win" else 0 for g in games]

# train, test = model_selection.train_test_split(games)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
clf = Perceptron(random_state=42)
clf.fit(X_train, y_train)
print("test accuracy of: ", clf.score(X_test, y_test))


# data = [g["teams"][team][attribute] for g in train]

# plt.hist(data)
# plt.show()
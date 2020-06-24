"""This is a prototype that displays different attributes of the feature vectors that have been obtained from the riot api. These features are
displayed as a distribution.
"""
import pymongo
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from sklearn.model_selection import train_test_split
AVG_WINRATE = 0.5169954315499581


team = 0

# first, we have to get the data from the mongodb store that's on summoner's rift (map id 11)
db = pymongo.MongoClient().datastore
docs = db.games.find({"gameMode":"CLASSIC"})
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

X = np.array(X)
y = np.array(y)
print("Training on data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
X_train, X_validate, y_train, y_validate = train_test_split(X_train, y_train, test_size=0.2)

layer_size = 200
activation = 'sigmoid'

inputs = keras.Input(shape=(20,))
x = layers.Dense(layer_size, activation=activation)(inputs)
x = layers.Dense(layer_size, activation=activation)(x)
x = layers.Dense(layer_size, activation=activation)(x)
x = layers.Dense(layer_size, activation=activation)(x)
x = layers.Dense(layer_size, activation=activation)(x)

outputs = layers.Dense(2, activation='sigmoid', name='predictions')(x)
model = keras.Model(inputs=inputs, outputs=outputs)

model.compile(
    optimizer=keras.optimizers.RMSprop(),
    loss=keras.losses.MeanAbsoluteError(),
    metrics=[keras.metrics.BinaryAccuracy()],
)




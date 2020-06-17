from leaguepredict.match_prediction.raw_data_loader import load_entries, load_summoners, load_games

load_entries("challenger")
load_entries("grandmaster")
load_entries("master")
load_entries("diamond", division="I")
load_entries("diamond", division="II")
load_entries("diamond", division="III")
load_entries("diamond", division="IV")
load_summoners()
load_games()
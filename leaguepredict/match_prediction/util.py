import requests
import yaml

with open("/home/sudarshan/projects/league-match-prediction/leaguepredict/match_prediction/config.yml", 'r') as config:
    config_data = yaml.safe_load(config)

API_URL = config_data["request_info"]["API_URL"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]


def get_summoner_id(summoner_name):
    """Gets the summoner id of a summoner_name"""
    r = requests.get(API_URL + "/lol/summoner/v4/summoners/by-name/" + summoner_name, headers=REQUEST_HEADERS)
    return r.json()["id"]


def get_participants(summoner_name):
    """Returns a list of participants involved in a game that the summoner_id is in by summoner_name.
    If the summoner_id isn't in a game, returns an empty list"""
    summoner_id = get_summoner_id(summoner_name)
    r = requests.get(API_URL + "/lol/spectator/v4/active-games/by-summoner/" + summoner_id, headers=REQUEST_HEADERS)
    if r.status_code != 200:
        return []
    else:
        data = r.json()
        return [p["summonerName"] for p in data["participants"]]

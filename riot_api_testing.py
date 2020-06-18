import requests
import yaml
import itertools


with open("leaguepredict/match_prediction/config.yml", 'r') as config:
    config_data = yaml.safe_load(config)

API_URL = config_data["request_info"]["API_URL"]
REQUEST_HEADERS = config_data["request_info"]["REQUEST_HEADERS"]


def make_request(tier, division, queue='RANKED_SOLO_5x5'):
    tier_request = {
        ("challenger", division): "/lol/league/v4/challengerleagues/by-queue/",
        ("grandmaster", division): "/lol/league/v4/grandmasterleagues/by-queue/",
        ("master", division): "/lol/league/v4/masterleagues/by-queue/",
        ("diamond", division): "/lol/league/v4/entries/{}/{}/{}".format(queue, tier.upper(), division)
    }
    if tier == "diamond":
        infinite = itertools.count(1)
        while True:
            page = next(infinite)
            r = requests.get(API_URL + tier_request[(tier, division)] + "?page={}".format(page),
                     headers=REQUEST_HEADERS)
            print(r)
            if r is not None:
                print(r.json())
            else:
                break


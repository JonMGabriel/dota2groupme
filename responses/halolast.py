# -*- coding: utf-8 -*
from AbstractResponse import AbstractResponse
import requests
import os
import json

class ResponseHaloLast(AbstractResponse):

    template = "{name} went {K},{D},{A} in Halo 5 finishing {rank}th Place and he {result}\n"

    result_legend = {0:"DNF (like a bitch do)", 1:"Lost, bitch!", 2:"Tied (still a bitch tho)", 3:"Won! :D"}
    halotracker_template = "http://halotracker.com/h5/games/{name}/{match_id}?page=0"

    RESPONSE_KEY = "#halolast"

    def __init__(self, msg):
        super(ResponseHaloLast, self).__init__(msg)

    def respond(self):
        out = ""
        canonical_name = (key for key,value in AbstractResponse.GroupMeIDs.items() if value==self.msg.sender_id).next()

        xbox_live_name = AbstractResponse.GroupMetoXboxName[canonical_name]

        halo_url = "https://www.haloapi.com/stats/h5/players/{name}/matches"
        key = "0"
        print(canonical_name)
        try:
            with open('local_variables.json') as f:
                local_var = json.load(f)
                key = local_var["HALO_KEY"]
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            key = os.getenv('HALO_KEY')
        except:
            print "Something went very wrong in #halolast for the Halo key"

        response = requests.get(halo_url.format(name=xbox_live_name), headers={'Ocp-Apim-Subscription-Key': key})

        last_match = response.json()["Results"][0]
        kills = last_match["Players"][0]["TotalKills"]
        death = last_match["Players"][0]["TotalDeaths"]
        assists = last_match["Players"][0]["TotalAssists"]
        result = last_match["Players"][0]["Result"]
        rank = last_match["Players"][0]["Rank"]
        result_str = ResponseHaloLast.result_legend[result]
        match_id = last_match["Id"]["MatchId"]
        username = last_match["Players"][0]["Player"]["Gamertag"]

        out += ResponseHaloLast.template.format(name=canonical_name, K=kills, A=assists, D=death, rank=rank, result=result_str)
        out += ResponseHaloLast.halotracker_template.format(name=username, match_id=match_id)
        return out



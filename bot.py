import os
import urllib2
import urllib
import traceback
import random
import local_data
import sys
from flask import Flask, request
from dota2py import api
from dota2py import data

DEBUG = False

key =  "63760574A669369C2117EA4A30A4768B"


help_dict = {"#last" : "Shows your personel stats from the last game, add a user argument to find someone elses stats",
           "#now" : "Shows who is currently online (NOT IMPLEMENTE YET)",
           "#setSteam" : "Set your SteamID if not hardcoded in yet. This is you Steam (Not Dota) username.",
           "#setDOTA" : "This is your Dota ID number. Find this as the last number in your DotaBuff URL",
           "#status" : "See if sUN bot is up",
           "#help" : "You are reading the help now...",
           "#next" : "Picks a random hero to play...",
           "#nextItem" : "Picks a random item to buy...",
           "#nextTeam" : "Picks a awesome team to play...",
}

app = Flask(__name__)
#
# https://api.groupme.com/v3/bots/post

def random_hero():
	next_hero = data.get_hero_name(random.randint(1, 107))
	if next_hero is not None:
		return str(next_hero["localized_name"])
	else:
		return random_hero()

		
def random_item():
	next_item = data.get_item_name(random.randint(1, 212))
	if next_item is not None:
		return str(next_item["name"])
	else:
		return next_item()


def send_message(msg):
	print "Sending " + msg
	if not DEBUG:
		url = 'https://api.groupme.com/v3/bots/post'
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		header = { 'User-Agent' : user_agent }
		values = {
    	  'bot_id' : '535cbd947cf38b46a83fa3084f',
    	  'text' : msg,
		}
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data, header)
		response = urllib2.urlopen(req)
		#print "msg"
		return response
	else:
		return 'Win'
	
def set_steam(msg, user):
	print "Got here"
	GroupMetoSteam[user] = msg
	return send_message("I set your Steam ID to: " + msg )
	
def set_dota(msg, user):
	print "Got here"
	GroupMetoDOTA[user] = msg
	return send_message("I set your Dota ID to: " + msg )
	

def last_game(msg, user):
	
	print "Starting"
	
	if not local_data.has_steamID(user):
		send_message("I don't know your SteamID! Set it with '#set ID'")
		return 'OK'
		
	if not local_data.has_dotaID(user):
		send_message("I don't know your DOTA ID! Set it with '#setDota ID'")
		return 'OK'
		
	print "Setting Key & Account ID"	
	api.set_api_key(key)

	account_id = local_data.name_to_steamID(user)
	
	print "Got Account ID"
	# Get a list of recent matches for the player
	matches = api.get_match_history(account_id=account_id)["result"]["matches"]

	#Get the full details for a match
	match = api.get_match_details(matches[0]["match_id"])
	print "Got Match Details"
	player_num = 0
	for x in match["result"]["players"]:
		if int(x["account_id"]) == local_data.name_to_dotaID(user):
			print "Got User Data"
			
			#Stats?
			print player_num
			send_message("As " + data.get_hero_name(x["hero_id"])["localized_name"] + " you went " + str(x["kills"]) + ":" + str(x["deaths"]) + ":" + str(x["assists"]) + " with " + str(x["gold_per_min"]) + " GPM finishing at level " + str(x["level"]))
			
			#Items?
			finalItems = "Your items: "
			for itemNum in range(0, 6):
				if x["item_" + str(itemNum)] != 0 and x["item_" + str(itemNum)] is not None:
					finalItems += str(data.get_item_name(x["item_" + str(itemNum)])["name"]) + ", "
			send_message(finalItems)
			
			#Win?
			if player_num < 5 and match["result"]["radiant_win"]:
				send_message("You Won!")
			else:
				send_message("You Lost.... Bitch")
		player_num = player_num +1	
	return 'OK'

def current_online(msg, user):
	return send_message("No one is online!")

def help(msg, user):
	send_message("Fuck you " + str(user) + "... This shit isn't that hard")
	for command, help_text in help_dict.iteritems():
		send_message(command + ": " + help_text)
	return 'OK'

def status(msg, user):
	return send_message("Currently listening...")

def next(msg, user):
	return send_message("You will play " + random_hero())
	
def nextItem(msg, user):
	return send_message("You will buy " + random_item())
	
def nextTeam(msg, user):
	return send_message("The best team ever: " + random_hero() + ", " + random_hero() + ", " + random_hero() + ", " + random_hero() + ", " + random_hero())	


options = {"#last" : last_game,
           "#now" : current_online,
           "#setSteam" : set_steam,
           "#setDOTA" : set_dota,
           "#status" : status,
           "#help" : help,
           "#next" : next,
           "#nextItem" : nextItem,
           "#nextTeam" : nextTeam,
}



@app.route('/message/', methods=['POST'])
def message():
	new_message = request.get_json(force=True)
	sender = new_message["name"]
	body = new_message["text"]
	if body.startswith("#"):
		print "Calling: " + body.partition(' ')[0] + " With " + body.partition(' ')[2]
		
		try:
			options[body.partition(' ')[0]](body.partition(' ')[2], sender)
		except BaseException as e:
			print repr(e)
    		traceback.print_exc()
	return 'OK'

@app.route("/")
def hello():
	return "Hello world!"

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == "debug":
			DEBUG = True
			
	port = int(os.environ.get("PORT", 5000))
	if not DEBUG:
		app.run(host='0.0.0.0', port=port)
	else:
		app.run(host='0.0.0.0', port=port, debug=True)
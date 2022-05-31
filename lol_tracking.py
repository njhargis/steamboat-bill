import os
import requests
import json
from threading import Thread
from replit import db

### Registering/Deregistering ###
# This function will add a summoner to our list to track, while grabbing info about them from Riot.
def register_account_info(summonerName):
  json_data = call_riot_api('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName)
  if(json_data == "Failed"):
    return "Failed to register info."
  else:
    summoner_id = json_data['id']
    account_id = json_data['accountId']
    puuid = json_data['puuid']
    accountExists = False
    # If account table exists already.
    if "accounts" in db.keys():
      # Do not let more than 20 summoners be registered.
      # This prevents us from hitting Riot's throttle limits.
      if len(db["accounts"]) >= 20:
        value = "The max number of summoners are registered."
        return value
      # Loop through accounts to see if this one already exists.
      for x in range(len(db["accounts"])):
        if summonerName in db["accounts"][x].keys():
          accountExists = True
          db["accounts"][x][summonerName] = [summoner_id, account_id, puuid]
          value = summonerName + ' is already registered.'
          return value
      # After looping through everything, account does not exist, so insert.
      if not accountExists:
        db["accounts"].append({summonerName: [summoner_id, account_id, puuid]})
    # Account table does not exist, create it and add new record.
    else:
      db["accounts"] = [{summonerName: [summoner_id, account_id, puuid]}]

    # Finally, return our message.
    value = summonerName + ' registered. Their games will now be tracked.'
    return value

# This function will remove a tracked summoner from our list.
def deregister_account_info(summonerName):
   # If account table exists already.
    if "accounts" in db.keys():
      # Rebuild db["accounts"] without this record, faster than removing iteratively each item since you have to "dig" to remove each to not leave orphans.
      db["accounts"] = [d for d in db["accounts"] if summonerName not in d.keys()]
      value = summonerName + ' deregistered. Their games will no longer be tracked.'
      return value
    # Account table does not exist, so they can't be registered.
    else:
      value = summonerName + ' is not registered.'
      return value

# This function lists our registered summoners
def registered_summoners():
  if "accounts" in db.keys():
    listOfSummoners = "We are tracking the following summoners."
    # Loop through accounts to find this one and remove it.
    for x in range(len(db["accounts"])):
      listOfSummoners += '\n' + str(db["accounts"][x].value).split("'", 3)[1]
    return listOfSummoners
      
### Polling for live games ###      
# This function will hit Riot's API to see if a specific summoner is in an active game.
def poll_live_games(encryptedSummonerId, store=None):
  if store is None:
    store = {}
  json_data = call_riot_api('https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/' + encryptedSummonerId)
  if(json_data == "Failed"):
    value = "Summoner is not in a game."
    store[encryptedSummonerId] = value
  else:
    game_type = json_data['gameType']
    player_count  = json_data['participants'].count
    #if(game_type == "MATCHED_GAME" or (game_type == "CUSTOM_GAME" and player_count == 10)):
    if(game_type == "MATCHED_GAME" or game_type == "CUSTOM_GAME"):
      start_time = json_data['gameStartTime']
      participants = json_data['participants']
      summoner = ''
      champion = ''
      # Loop through all participants
      for x in range(len(participants)):
        summonerId = participants[x].get("summonerId")
        print(summonerId)
        if summonerId == encryptedSummonerId:
          summoner = participants[x].get("summonerName")
          champion = participants[x].get("championId")
      value = str(summoner) + ' is in a League of Legends game! The match started around' + calc_time_since(start_time) + ' minutes ago. They locked in ' + str(champion) + '. | startTime: ' + str(start_time)
    store[encryptedSummonerId] = value
  return store

# This "main" function will go through all of our registered summoners and spawn a thread to check their status
def threaded_poll_all_registered_summoners():
  store = {}
  threads = []
  # If account table exists already.
  if "accounts" in db.keys():
    # Loop through accounts to create a thread for each one.
    for x in range(len(db["accounts"])):
      summonerName = str(db["accounts"][x].value).split("'", 3)[1]
      summonerId = db["accounts"][x][summonerName][0]
      t = Thread(target=poll_live_games, args=(summonerId, store)) 
      threads.append(t)

    # start the threads
    [ t.start() for t in threads ]
    # wait for the threads to finish
    [ t.join() for t in threads ]
    print(store)
    return store
          
  
### Base Functionality ###
# Standard code to hit riot API with key in header.      
def call_riot_api(path):
  headers = {'X-Riot-Token': os.getenv('RIOT_TOKEN')}
  response = requests.get(path, headers=headers);
  if(response.status_code != 200):
    return "Failed"
  else:
    json_data = json.loads(response.text)
    return json_data

# This isn't very accurate due to mistimings, ideally we'd call this at message print time.
def calc_time_since(time_value):
  millisec = time.time() * 1000
  difference = round((millisec - time_value) / 1000 / 60)
  return str(difference)
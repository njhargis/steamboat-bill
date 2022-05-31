import discord
import os
import requests
import json
from replit import db
from twisted.internet import task, reactor

###############
# To-do:
# 1) Make looping through accounts async
# 2) Limit number of registered summoners possible
# 3) List all registered summoners
###############

### Registering/Deregistering ###
# This function will add a summoner to our list to track, while grabbing info about them from Riot.
def register_account_info(summonerName):
  json_data = call_riot_api('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName)
  if(json_data == "Failed"):
    return "Failed to register info."
  else:
    account_id = json_data['accountId']
    puuid = json_data['puuid']
    accountExists = False
    # If account table exists already.
    if "accounts" in db.keys():
      # Loop through accounts to see if this one already exists.
      for x in range(len(db["accounts"])):
        if summonerName in db["accounts"][x].keys():
          accountExists = True
          db["accounts"][x][summonerName] = [account_id, puuid]
          value = summonerName + ' is already registered.'
          return value
      # After looping through everything, account does not exist, so     insert.
      if not accountExists:
        db["accounts"].append({summonerName: [account_id, puuid]})
    # Account table does not exist, create it and add new record.
    else:
      db["accounts"] = [{summonerName: [account_id, puuid]}]

    # Finally, return our message.
    value = summonerName + ' registered. Their games will now be tracked.'
    return value

# This function will remove a tracked summoner from our list.
def deregister_account_info(summonerName):
   # If account table exists already.
    if "accounts" in db.keys():
      accountExists = False
      # Loop through accounts to find this one and remove it.
      for x in range(len(db["accounts"])):
        if summonerName in db["accounts"][x].keys():
          accountExists = True
          del db["accounts"][x][summonerName]
          value = summonerName + ' deregistered. Their games will no longer be tracked.'
          return value
      # After looping through everything, account does not exist, so let them know.
      if not accountExists:
        value = summonerName + ' is not registered.'
        return value
    # Account table does not exist, so they can't be registered.
    else:
      value = summonerName + ' is not registered.'
      return value

### Polling for live games ###      
# This function will hit Riot's API to see if a specific summoner is in an active game.
def poll_live_games(encryptedSummonerId):
  json_data = call_riot_api('https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/' + encryptedSummonerId)
  if(json_data == "Failed"):
    return "Summoner is not in a game."
  else:
    game_type = json_data['gameType']
    player_count  = json_data['participants'].count
    #if(game_type == "MATCHED_GAME" or (game_type == "CUSTOM_GAME" and player_count == 10)):
    if(game_type == "MATCHED_GAME" or game_type == "CUSTOM_GAME"):
      start_time = json_data['gameStartTime']
      champion = json_data['championId']
      summoner = encryptedSummonerId
      value = summoner + ' just started a League match at ' + start_time + '. They locked in ' + champion + '.'
      return value

# This function will go through all of our registered summoners and check their status
def check_registered_summoners():
  # If account table exists already.
    if "accounts" in db.keys():
      # Loop through accounts to poll each one.
      # This should be async
      for x in range(len(db["accounts"])):
        print(db["accounts"][x].value)
        
          
  
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

# Create a Discord client.
client = discord.Client()
    
# This will listen for a message event on the Discord server.
@client.event
async def on_message(message):
  # Ignore messages from the bot itself
  if message.author == client.user:
    return
  
  # Command !summoner
  if (message.content.startswith('!summoner') or message.content.startswith("/summoner")):
    messageContent = poll_live_games('n2CdunbUgnxL5bXxPWYWEvKSYdf0Ropy7fvshbNSdkNdSWk')
    await message.channel.send(messageContent)
      
  # Command !register-summoner
  if message.content.startswith("/register-summoner"):
    summoner_name = message.content.split("/register-summoner ",1)[1]
    messageContent = register_account_info(summoner_name)
    await message.channel.send(messageContent)

  # Command !deregister-summoner
  if message.content.startswith("/deregister-summoner"):
    summoner_name = message.content.split("/deregister-summoner ",1)[1]
    messageContent = deregister_account_info(summoner_name)
    await message.channel.send(messageContent)

# Run this code on your discord app/bot.
client.run(os.getenv('DISCORD_TOKEN'))

# Set our timeout for how often to poll (in seconds)
timeout = 120.0

# Looping call to call this after timeout period.
l = task.LoopingCall(poll_live_games('n2CdunbUgnxL5bXxPWYWEvKSYdf0Ropy7fvshbNSdkNdSWk'))
l.start(timeout)

reactor.run()
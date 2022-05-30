import discord
import os
import requests
import json
from replit import db

client = discord.Client()

summoner_names = {'ßirdd', 'kpvols', 'WeinerCleaner', 'DirtyNuech', 'Dip Wickler', 'Śaint', 'Bhad Beetle', 'Moon Beetle', 'Sun Beetle', 'imlwl', 'Gusgusgusgusgus', 'DolphinTeeth', 'Sealane'}

print(db.keys())
print(db["accounts"])
del db["accounts"]

def register_account_info(summonerName):
  json_data = call_riot_api('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName)
  if(json_data == "Failed"):
    return "Failed to register info."
  else:
    account_id = json_data['accountId']
    puuid = json_data['puuid']
    if "accounts" in db.keys():
      #TO-DO: don't insert duplicates, update the original.
      db["accounts"].append({summonerName: [account_id, puuid]})
    else:
      db["accounts"] = [{summonerName: [account_id, puuid]}]

    #If our db already has a table for accounts, append value
    #if "accounts" in db.keys():   
    #  db["accounts"].append({summonerName: {account_id, puuid}})
      
    #Otherwise, create a table for accounts
    #else:
    #  db["accounts"] = [{summonerName: {account_id, puuid}}]
      
    value = summonerName + ' registered. Account Id:' + account_id + '. PUUID: ' + puuid + '.'
    return value
    
#This function will poll Riot's API to see if the summoner is in an active game.
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

#Standard code to hit riot API with key in header.
def call_riot_api(path):
  headers = {'X-Riot-Token': os.getenv('RIOT_TOKEN')}
  response = requests.get(path, headers=headers);
  if(response.status_code != 200):
    return "Failed"
  else:
    json_data = json.loads(response.text)
    return json_data



  
#This will listen for a message event on the discord server.
@client.event
async def on_message(message):
  #Ignore messages from the bot itself
  if message.author == client.user:
    return
  
  #if they call command !summoner
  if (message.content.startswith('!summoner') or message.content.startswith("/summoner")):
    messageContent = poll_live_games('n2CdunbUgnxL5bXxPWYWEvKSYdf0Ropy7fvshbNSdkNdSWk')
    await message.channel.send(messageContent)
      
  #if they call command !register
  if (message.content.startswith("!register") or message.content.startswith("/register")):
    messageContent = register_account_info("ßirdd")
    await message.channel.send(messageContent)
    #for s in summoner_names:
      #sumName, acct, puuid = register_account_info(s)
      #await message.channel.send(smnName + ' registered. Account Id:' + acct + '. PUUID: ' + puuid + '.')
      #print(s)

  
    

#Run this code on your discord app/bot.
client.run(os.getenv('DISCORD_TOKEN'))
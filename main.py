import discord
import os
import requests
import json
from replit import db

client = discord.Client()

summoner_names = {'ßirdd', 'kpvols', 'WeinerCleaner', 'DirtyNuech', 'Dip Wickler', 'Śaint', 'Bhad Beetle', 'Moon Beetle', 'Sun Beetle', 'imlwl', 'Gusgusgusgusgus', 'DolphinTeeth', 'Sealane'}

def register_account_info(summonerName):
  json_data_string = call_riot_api('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonerName)
  print(json_data_string)
  if(json_data_string != "Failed"):
    return
  else:
    json_data = json.loads(json_data_string)
    account_id = json_data['accountId']
    puuid = json_data['puuid']
    print(summonerName)
    print(puuid)
    print(account_id)
    #If our db already has a table for accounts, append value
    #if "accounts" in db.keys():
    #  accounts = db["accounts"]
    #  accounts.append(summonerName, account_id, puuid)
    #  db["accounts"] = accounts
    #Otherwise, create a table for accounts
    #else:
    #  db["accounts"] = [summonerName, account_id, puuid]

    return summonerName, account_id, puuid
    
#This function will poll Riot's API to see if the summoner is in an active game.
def poll_live_games(encryptedSummonerId):
  json_data_string = call_riot_api('https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/' + encryptedSummonerId)
  print(json_data_string)
  if(json_data_string != "Failed"):
    return
  else:
    json_data = json.loads(json_data_string)
    print(json_data)
    game_type = json_data['gameType']
    print(game_type)
    player_count  = json_data['participants'].count
    print(player_count)
    #if(game_type == "MATCHED_GAME" or (game_type == "CUSTOM_GAME" and player_count == 10)):
    if(game_type == "MATCHED_GAME" or game_type == "CUSTOM_GAME"):
      start_time = json_data['gameStartTime']
      champion = json_data['championId']
      summoner = encryptedSummonerId
      print(start_time)
      print(champion)
      print(summoner)
      return start_time, champion, summoner

#Standard code to hit riot API with key in header.
def call_riot_api(path):
  headers = {'X-Riot-Token': os.getenv('RIOT_TOKEN')}
  response = requests.get(path, headers=headers);
  if(response.status_code != 200):
    return "Failed"
  else:
    return response.text



  
#This will listen for a message event on the discord server.
@client.event
async def on_message(message):
  #Ignore messages from the bot itself
  if message.author == client.user:
    return
  
  #if they call command !summoner
  if (message.content.startswith('!summoner') or message.content.startswith("/summoner")):
    smnName, matchTime, champName = poll_live_games('n2CdunbUgnxL5bXxPWYWEvKSYdf0Ropy7fvshbNSdkNdSWk')
    await message.channel.send(smnName + ' just started a League match at ' + matchTime + '. They locked in ' + champName + '.')
      
  #if they call command !register
  if (message.content.startswith("!register") or message.content.startswith("/register")):
    #smnName, acct, puuid = register_account_info("ßirdd")
    #await message.channel.send(smnName + ' registered. Account Id:' + acct + '. PUUID: ' + puuid + '.')
    for s in summoner_names:
      sumName, acct, puuid = register_account_info(s)
      #await message.channel.send(smnName + ' registered. Account Id:' + acct + '. PUUID: ' + puuid + '.')
      #print(s)

  
    

#Run this code on your discord app/bot.
client.run(os.getenv('DISCORD_TOKEN'))
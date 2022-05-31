import discord
import os
import schedule
import time
from keep_alive import keep_alive
from lol_tracking import *


###############
# To-do:
# 1) Make polling our threaded requests happen every 5 minutes
###############
# Shoutouts
# https://stackoverflow.com/questions/16982569/making-multiple-api-calls-in-parallel-using-python-ipython
# https://developer.riotgames.com/apis
###############


  
# Create a Discord client.
client = discord.Client()
    
# This will listen for a message event on the Discord server.
@client.event
async def on_message(message):
  # Ignore messages from the bot itself
  if message.author == client.user:
    return
        
  # Command /register-summoner
  if message.content.startswith("/register-summoner"):
    summoner_name = message.content.split("/register-summoner ",1)[1]
    messageContent = register_account_info(summoner_name)
    await message.channel.send(messageContent)

  # Command /deregister-summoner
  if message.content.startswith("/deregister-summoner"):
    summoner_name = message.content.split("/deregister-summoner ",1)[1]
    messageContent = deregister_account_info(summoner_name)
    await message.channel.send(messageContent)

  # Command /summoners
  if message.content.startswith("/summoners"):
    messageContent = registered_summoners()
    await message.channel.send(messageContent)

#Poll our accounts every minute.
schedule.every(1).minutes.do(threaded_poll_all_registered_summoners)
  
while True:
    schedule.run_pending()
    time.sleep(1)
    
#This keeps the web server up.
keep_alive()
    
# Run this code on your discord app/bot.
client.run(os.getenv('DISCORD_TOKEN'))
  

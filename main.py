import discord
import os
import schedule
import time
from keep_alive import keep_alive
from discord.ext import commands
from lol_tracking import *
from steamboat_commands import *
import asyncio
from concurrent.futures import ProcessPoolExecutor


# Shoutouts
# https://stackoverflow.com/questions/16982569/making-multiple-api-calls-in-parallel-using-python-ipython
# https://developer.riotgames.com/apis
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/
# DADAM
# https://betterprogramming.pub/how-to-make-discord-bot-commands-in-python-2cae39cbfd55
###############

def run_bot():
  bot = commands.Bot(command_prefix="/", case_insensitive=True)
  
  # When our bot first joins a server.
  @bot.event
  async def on_ready():
    print('{0.user} is here to raid and plunder.'.format(bot))
  
  # This is where we hold the entry point to our bot/commands.
  @bot.command(name='ping', brief="Pongs your ping", description="Pongs you ping description")
  async def ping(ctx):
    await ctx.channel.send("pong")
  
  @bot.command(name='register-summoner', brief="Registers a summoner to be tracked.", 
               description="Registers a summoner name, which then tracks their matches, to post when they join a match and the results of the match. Only accepts one summoner name at a time.")
  async def registerSummonerCommand(ctx, *, arg):
    await registerSummoner(ctx, arg)
    
  @bot.command(name='deregister-summoner', brief="Deregisters a summoner who is being tracked.", 
               description="If the given summoner name is already being tracked, removes them from the list so their matches are no longer posted. Only accepts one summoner name at a time.")
  async def deregisterSummonerCommand(ctx, *, arg):
    await deregisterSummoner(ctx, arg)
  
  @bot.command(name='list-summoners', brief="Lists all registered summoners.", 
               description="Lists all the summoner names that are being tracked.")
  async def listSummonersCommand(ctx):
    await listSummoners(ctx)
      
  #This keeps the web server up.
  keep_alive()
    
  # Run this code on your discord app/bot.
  bot.run(os.getenv('DISCORD_TOKEN'))

def polling_every_x():
  #Poll our accounts every minute.
  schedule.every(1).minutes.do(threaded_poll_all_registered_summoners)
    
  while True:
      schedule.run_pending()
      time.sleep(1)

if __name__ == "__main__":
    executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, run_bot)
    loop.run_in_executor(executor, polling_every_x)

    loop.run_forever()
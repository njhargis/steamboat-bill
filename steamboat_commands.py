import discord
from discord.ext import commands
import operator
from replit import db
from lol_tracking import *

### Commands ###
# This is where we hold all code that pertains to what the command does in discord
# Do not put command specific logic here.
################

async def registerSummoner(ctx, summonerName):
  messageContent = register_account_info(summonerName)
  await ctx.message.channel.send(messageContent)

async def deregisterSummoner(ctx, summonerName):
  messageContent = deregister_account_info(summonerName)
  await ctx.message.channel.send(messageContent)

async def listSummoners(ctx):
  messageContent = registered_summoners()
  await ctx.message.channel.send(messageContent)
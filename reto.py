# Import global variables and databases.
from definitions import bottoken, botname, botver, prefix, debug, db, srv, activity, customprefix

# Imports, database definitions and all that kerfuffle.

import discord
from discord.ext import commands, tasks
import asyncio
import pyfiglet
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract, delete
import aiohttp        
import aiofiles
import os.path
import os
import json
import random
from datetime import datetime, date
import logging
import traceback
import sys

# sharedFunctions
from sharedFunctions import printLeaderboard, createLeaderboardEmbed, getProfile, sendErrorEmbed, reactionAdded, reactionRemoved

# ----------------------------------------------------------------------------------------------

getactivities = activity.all()
botactivity = []
i = 0
for value in getactivities:
	botactivity.append(getactivities[i]["activity"])
	i += 1

def get_prefix(bot, msg):
	customprefix.clear_cache()
	if not msg.guild: # is on DMs
		return commands.when_mentioned_or(prefix)(bot,msg)
	else:
		pre = customprefix.search(Query().server == msg.guild.id)
		if pre:
			return pre[0]["prefix"] # custom prefix on json db
		else:
			return prefix # default prefix

bot = commands.Bot(command_prefix=get_prefix)
client = discord.Client()
ascii_banner = pyfiglet.figlet_format(botname)

@bot.command
async def load(ctx, extension):
	bot.load_extension(f'cogs.{extension}')

@bot.command
async def unload(ctx, extension):
	bot.unload_extension(f'cogs.{extension}')

@bot.event
async def on_raw_reaction_add(payload):
	await reactionAdded(bot, payload)

@bot.event
async def on_raw_reaction_remove(payload):
	await reactionRemoved(bot, payload)

for file in os.listdir("./cogs"):
	if file.endswith(".py"):
		bot.load_extension(f'cogs.{file[:-3]}') #[:-3] removes the last 3 chars

# Error handler.
@bot.event
async def on_command_error(ctx, error):
	ignored = (commands.CommandNotFound, )
	error = getattr(error, 'original', error)
	if isinstance(error, ignored):
		return
	if isinstance(error, discord.ext.commands.CommandNotFound):
		return
	if isinstance(error, discord.ext.commands.DisabledCommand):
		await sendErrorEmbed(ctx, f'{ctx.command} has been disabled.')
	elif isinstance(error, discord.ext.commands.NoPrivateMessage):
		try:
			await sendErrorEmbed(ctx.author, f'{ctx.command} can not be used in Private Messages.')
		except discord.HTTPException:
			pass
	elif isinstance(error, commands.BadArgument):
		if ctx.command.qualified_name == 'tag list':
			await sendErrorEmbed(ctx, "Can't find that member, for whatever reason. Please try again.")
	elif isinstance(error, discord.ext.commands.errors.MissingPermissions):
		await sendErrorEmbed(ctx, "You're missing the required permissions to run this command!")
	else:
		print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
		traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	raise error

@bot.event
async def on_ready():

	# Warning for users who've yet to migrate to the new database system.
	olddb = TinyDB("json/db.json")
	if ((not db) and (olddb)):
		print(pyfiglet.figlet_format("READ THIS!"))
		print("Hey there, " + botname + " admin!\nIf you're reading this, we've detected you've got the JSON databases from v1.5.2 and below, but have yet to populate the new ones.\nWe may have done a false positive, though. If this is your first time using " + botname + ", and you've started with v1.6 or higher, welcome aboard!\nPlease dismiss this message.\nIf not, here's the deal: v1.6 implements a new database system that's completely encrypted, to allow for more security of the data " + botname + " stores.\nHowever, this migration ISN'T DONE BY DEFAULT. If you want to use v1.6 and higher, you might want to import your databases to the new .reto filesystem!\n\nTo do so, please run 'python encrypt-databases.py' on the same folder as  " + botname + "'s.\nThis won't be destructive - your old DB previous to this update will still be around, but the new system will be used!\n\nThat's it. Thank you for using " + botname + "!\n\n")
		print ("--------------------------------------------")

	print (ascii_banner)
	print (botname + " is ONLINE!")
	if len(bot.guilds) == 1:
		print ("Running with the name " + str(bot.user) + " on " + str(len(bot.guilds)) + " server")
	else:
		print ("Running with the name " + str(bot.user) + " on " + str(len(bot.guilds)) + " servers")
	if debug:
		print ('WARNING: You\'re running ' + str(botname)+ ' on Debug Mode. Remember to change the Debug variable in json/config.json to "False" later!')
	print ("Invite link: https://discordapp.com/api/oauth2/authorize?client_id=" + str(bot.user.id) + "&permissions=1342449744&scope=bot")
	print ("Ver " + botver + " - check the updates with ?changelog")
	print ("?setup to get started!")
	print ("--------------------------------------------")

	async def on_guild_post():
		print("Server count posted successfully")

	global botactivity
	if not botactivity:
		botactivity = [prefix + 'setup to get started!', 'Hey, bot owner - change the default activities with ' + prefix + 'activity!']
	if botver != "":
		game = discord.Game(botactivity[random.randrange(len(botactivity))] + " | v" + botver)
	else:
		game = discord.Game(botactivity[random.randrange(len(botactivity))])
	await bot.change_presence(activity=game)
	bot.loop.create_task(statusupdates())

@bot.event
async def on_guild_join(guild):
	srv.upsert({'serverid': guild.id, 'heart': 'plus', 'crush': 'minus', 'star': '10', 'global': True}, Query().serverid == guild.id)
	for channel in guild.text_channels:
		if channel.permissions_for(guild.me).send_messages:
			embed=discord.Embed(title="Thank you for inviting " + botname + "!", description="Try using the ?setup command to get started!\nIf any problems arise, [join our Discord server](https://google.com) so we can give you a hand.")
			embed.set_thumbnail(url="https://i.ibb.co/ySfQhDG/reto.png")
			await channel.send(embed=embed)
		break

async def statusupdates():
	while True:
		await asyncio.sleep(60)

		# update the activity list
		activity.clear_cache()
		getactivities = activity.all()
		i = 0
		botactivity = []
		for value in getactivities:
			botactivity.append(getactivities[i]["activity"])
			i += 1
		if not botactivity:
			botactivity = [prefix + 'setup to get started!', 'Hey, bot owner - change the default activities with ' + prefix + 'activity!']
		if botver != "":
			game = discord.Game(botactivity[random.randrange(len(botactivity))] + " | v" + botver)
		else:
			game = discord.Game(botactivity[random.randrange(len(botactivity))])
		await bot.change_presence(activity=game)	

bot.run(bottoken)
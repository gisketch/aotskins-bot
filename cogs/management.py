# Import global variables and databases.
from definitions import botname, botowner, activity, post, priv

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
from datetime import datetime

# sharedFunctions
from sharedFunctions import printLeaderboard, createLeaderboardEmbed, getProfile, sendErrorEmbed, getCurrentPrefix

# ----------------------------------------------------------------------------------------------

class Management(commands.Cog):
	"""
	Commands that have to do with the bot's upkeep. Not relevant to normal users.
	"""

	isDeletingComments = False
	isFirstTime = True

	def __init__(self, client):
		self.client = client
		# Global variable related to periodical comment deletion.
		self.commentDeleter.start()

	def cog_unload(self):
		self.commentDeleter.cancel()
	
	#-------------------------
	#   MANAGEMENT COMMANDS
	#-------------------------
	@commands.command()
	async def activity(self,ctx,*args):
		"""[BOT ADMIN ONLY] Change the bot's activity."""

		prefix = await getCurrentPrefix(ctx)
		isOwner = False
		for x in botowner:
			if (int(ctx.message.author.id) == int(x)):
				isOwner = True

		if isOwner:
			if not args:
				embed = await showActivityList(ctx)
				glb = await ctx.send(embed=embed)
			if args[0] == "create":
				if len(args) == 1:
					await sendErrorEmbed(ctx, "Please introduce the text of the activity to be created.")
				else:
					activity.insert({'activity': args[1]})
					await ctx.send('The activity "' + args[1] + '" has been added to the list!')
			elif args[0] == "delete":
				if len(args) == 1:
					await sendErrorEmbed(ctx, "Please introduce the ID of the activity to be deleted. _You can check it doing " + prefix + "activity_.")
				else:
					# if len of activity equals 1 then dont let it remove
					try:
						toDelete = [int(args[1])]
						activity.remove(doc_ids=toDelete)
					except:
						await sendErrorEmbed(ctx, "The activity with the ID " + args[1] + " couldn't be deleted. (Double check if it exists?)")
					else:
						await ctx.send('The activity with the ID ' + args[1] + ' has been deleted.')
			else:
				embed = await showActivityList(ctx)
				glb = await ctx.send(embed=embed)
		else:
			await sendErrorEmbed(ctx, "Looks like you don't have permission to do this?\n_Are you hosting " + botname + "? If so make sure your User ID is on the **botowner** array on the config.json file!_")
	
	#-------------------------
	#      POST DELETER
	#-------------------------
	@tasks.loop(hours=12)
	async def commentDeleter(self):
		# Running Reto in an unverified bot (100 servers or less)? You can get rid of this function.
		if self.isDeletingComments == False and self.isFirstTime == False:
			print("Running the COMMENT DELETER...\nThis checks every 12 hours for saved comments that are 30 days old and deletes them from the comments.reto file,\nper Discord's verification rules. Do not stop " + botname + " while this is running!")
			postLength = len(post)
			self.isDeletingComments = True # Don't run it twice at the same time!
			i = 0
			totalDeleted = 0
			for postelement in post:
				i = i + 1
				print("Scanning the comments... (" + str(i) + "/" + str(postLength) + ")", end="\r")
				if not "timestamp" in postelement:
					post.update({"timestamp": str(datetime.now())}, where('msgid') == postelement['msgid'])
					postelement['timestamp'] = str(datetime.now())
				parsedTimestamp = datetime.strptime(postelement['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
				delta = datetime.now() - parsedTimestamp

				# permastorage
				privSettings = priv.search(Query().username == int(postelement['username']))
				if privSettings:
					privSettings = privSettings[0]
				if not privSettings or "storage" in privSettings and privSettings['storage'] == False or not "storage" in privSettings:
					if delta.days >= 30:
						totalDeleted = totalDeleted + 1
						post.remove(where('msgid') == postelement['msgid'])
			print("\nAll set! " + str(totalDeleted) + " comments were deleted.\n")
			self.isDeletingComments = False
		self.isFirstTime = False

async def showActivityList(ctx):

	prefix = await getCurrentPrefix(ctx)
	activity.clear_cache()
	result = activity.all()
	s = ""

	if result:
		for value in result: 
			s += ("ID: " + str(value.doc_id) + " - " + value["activity"] + "\n")
	embed = discord.Embed(title="List of Activities", colour=discord.Colour(0xa353a9), description=s)
	embed.set_footer(text="Add more with " + prefix + "activity create '[text]', or remove one with " + prefix + "activity delete [id].")
	return embed
			
def setup(client):
	client.add_cog(Management(client))
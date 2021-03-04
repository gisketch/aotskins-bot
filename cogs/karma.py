# Import global variables and databases.
from definitions import db, post

# Imports, database definitions and all that kerfuffle.

import discord
from discord.ext import commands, tasks
from discord.ext.tasks import loop
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

# sharedFunctions
from sharedFunctions import printLeaderboard, createLeaderboardEmbed, getProfile, sendErrorEmbed, getCurrentPrefix

# ----------------------------------------------------------------------------------------------

class Karma(commands.Cog):
	"""
	Karma counts and leaderboards and popular posts, oh my!
	"""
	def __init__(self, client):
		self.client = client
		self.updatelb.start()
	
	# -------------------------
	#	      ?PROFILE
	# -------------------------

	@commands.command(aliases=['thanks', 'points', 'point'], description="Check the accumulated amount of points (Karma) a given user has, among with other stats! Ping to check another user's karma account.")
	async def profile(self, ctx, *args):
		"""Check your (or others') profile, with info about your karma total and more!"""

		prefix = await getCurrentPrefix(ctx)
		if not args:
			await getProfile(ctx.message.author, ctx, self)
		elif not ctx.message.mentions:
			await sendErrorEmbed(ctx, "Invalid command! Use **" + prefix + "profile** to find out about your score, or @mention another user to get their score.")
		else:
			await getProfile(ctx.message.mentions[0], ctx, self)

	# -------------------------------
	#	    ?GLOBALLEADERBOARD
	# -------------------------------
	
	@commands.command(aliases=['glb'], description="Check the top 10 users of Discord! May take a while to load.\nYour username/score isn't showing up on the leaderboards? Update 1.2.1 made it so servers you're in and your score are joined together. This will refresh the next time someone hearts/crushs/stars one of your comments.")
	async def globalleaderboard(self, ctx, *args):
		"""Check the top karma holders on all Discord!"""
		db.clear_cache()
		result = db.all() # "Result" is just the entire database.
		leaderboard = {} # Prepares an empty dictionary.
		for x in result: # For each entry in the database:
			leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		s = ""
		i = 0
		for key, value in leaderboard: # For each value in the new, sorted DB:
			if not args:
				if i != 10:
					user = self.client.get_user(key)
					if not user:
						user = await self.client.fetch_user(key)
						print("User not found. Trying to fetch it...")
					if i==0:
						s += ("🥇 " + str(user) + " - " + str(value) +" Karma\n")
					elif i==1:
						s += ("🥈 " + str(user) + " - " + str(value) +" Karma\n")
					elif i==2:
						s += ("🥉 " + str(user) + " - " + str(value) +" Karma\n")
					else:
						s += ("✨ " + str(user) + " - " + str(value) +" Karma\n")
					i = i+1
			elif args[0] == "all":
				user = self.client.get_user(key)
				if not user:
					user = await self.client.fetch_user(key)
					print("User not found. Trying to fetch it...")
				if i==0:
					s += ("🥇 #" + str(i+1) + " - " + str(user) + " - " + str(value) +" Karma\n")
				elif i==1:
					s += ("🥈 #" + str(i+1) + " - "  + str(user) + " - " + str(value) +" Karma\n")
				elif i==2:
					s += ("🥉 #" + str(i+1) + " - "  + str(user) + " - " + str(value) +" Karma\n")
				else:
					s += ("✨ #" + str(i+1) + " - "  + str(user) + " - " + str(value) +" Karma\n")
				i = i+1
		embed = discord.Embed(title="Global Leaderboard", colour=discord.Colour(0xa353a9), description=s)
		glb = await ctx.send(embed=embed)

	# --------------------------
	#	    ?LEADERBOARD
	# --------------------------
	
	@commands.command(aliases=['lb', 'llb'], description="Check the top 10 users of your server! May take a while to load.\nYour username/score isn't showing up on the leaderboards? Update 1.2.1 made it so servers you're in and your score are joined together. This will refresh the next time someone hearts/crushs/stars one of your comments.")
	async def leaderboard(self, ctx, *args):
		"""Check this server's users with the most karma."""
		db.clear_cache()
		User = Query()
		server = str(ctx.message.guild.id)
		result = db.search(User.servers.all([server])) # doesnt work
		leaderboard = {} # Prepares an empty dictionary.
		for x in result: # For each entry in the database:
			leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		s = "Top artists sorted by most thanks received.\n\n"
		i = 0
		for key, value in leaderboard: # For each value in the new, sorted DB:
			if not args:
				if i != 10:
					user = self.client.get_user(key)
					
					if not user:
						user = await self.client.fetch_user(key)
						print("User not found. Trying to fetch it...")
					if i==0:
						s += ("🥇 #" + str(i+1) + " - " + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					elif i==1:
						s += ("🥈 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					elif i==2:
						s += ("🥉 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					else:
						s += ("🎨 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					i = i+1
		embed = discord.Embed(title="AOTSKINS Leaderboard", colour=discord.Colour(0xa353a9), description=s)
		glb = await ctx.send(embed=embed)

	# --------------------------
	#	    ?LEADERBOARD TOP 50 PERIODIC
	# --------------------------
	
	@tasks.loop(seconds=3600)
	async def updatelb(self,):
		"""Check this server's users with the most karma."""
		db.clear_cache()
		User = Query()
		server = str(811586984879063050)
		result = db.search(User.servers.all([server])) # doesnt work
		leaderboard = {} # Prepares an empty dictionary.
		for x in result: # For each entry in the database:
			leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		dateToday = "....."
		s = f"Top 50 artists sorted by most thanks received.\n\n"
		i = 0
		for key, value in leaderboard: # For each value in the new, sorted DB:
			if i != 50:
				user = self.client.get_user(key)
				if not user:
					user = await self.client.fetch_user(key)
				if i==0:
					s += ("🥇 #" + str(i+1) + " - " + f"<@!{key}>" + " - " + str(value) +" thanks\n")
				elif i==1:
					s += ("🥈 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
				elif i==2:
					s += ("🥉 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
				else:
					s += ("🎨 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
				i = i+1
		embed = discord.Embed(title="AOTSKINS' Top 50 Artists", colour=discord.Colour(0xa353a9), description=s)
		embed.set_footer(text='The list is last updated every hour.')

		thisguild = self.client.get_guild(811586984879063050)
		channel = discord.utils.get(thisguild.text_channels, name="top-50")
		lbMessage = await channel.fetch_message(815960589125287966)

		updatechannel = discord.utils.get(thisguild.text_channels, name="bot-commands")
		staffchannel = discord.utils.get(thisguild.text_channels, name="staff-commands")

		glb = await lbMessage.edit(embed=embed)
		await updatechannel.send(content=f"<#815956314798424114> leaderboard updated")
		await staffchannel.send(content=f"<#815956314798424114> leaderboard updated")

	# --------------------------
	#	    ?LEADERBOARD PROTOTYPE
	# --------------------------
	
	@commands.command(aliases=['lbtest'], description="Check the top 10 users of your server! May take a while to load.\nYour username/score isn't showing up on the leaderboards? Update 1.2.1 made it so servers you're in and your score are joined together. This will refresh the next time someone hearts/crushs/stars one of your comments.")
	async def leaderboard(self, ctx, *args):
		"""Check this server's users with the most karma."""
		db.clear_cache()
		User = Query()
		server = str(ctx.message.guild.id)
		result = db.search(User.servers.all([server])) # doesnt work
		leaderboard = {} # Prepares an empty dictionary.
		for x in result: # For each entry in the database:
			leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		s = "Top artists sorted by most thanks received.\n\n"
		i = 0
		for key, value in leaderboard: # For each value in the new, sorted DB:
			if not args:
				if i != 10:
					user = self.client.get_user(key)
					if not user:
						user = await self.client.fetch_user(key)
						print("User not found. Trying to fetch it...")
					if i==0:
						s += ("🥇 #" + str(i+1) + " - " + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					elif i==1:
						s += ("🥈 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					elif i==2:
						s += ("🥉 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					else:
						s += ("🎨 #" + str(i+1) + " - "  + f"<@!{key}>" + " - " + str(value) +" thanks\n")
					i = i+1
		embed = discord.Embed(title="AOTSKINS Leaderboard", colour=discord.Colour(0xa353a9), description=s)
		glb = await ctx.send(embed=embed)
		
	# ---------------------------------
	#	    ?GPLB (GLOBAL POST LB)
	# ---------------------------------
	
	@commands.command(aliases=['gplb', 'globalpostleaderboards'], description="Check the top 10 posts of all time on every server! May take a while to load. By default, it doesn't show comments posted in Not Safe for Work channels - ?gplb nsfw will let you see NSFW posts only, and ?gplb all will let you see both NSFW and SFW posts.")
	async def globalpostleaderboard(self, ctx, *args):
		"""Check the toppest posts on every guild!"""
		if not args:
			result = post.all() # "Result" is just the entire database.
		else:
			if ctx.message.mentions:
				valor = str(ctx.message.mentions[0].id)
				print(valor)
				result = post.search(Query()['username'] == valor) 
			else:
				result = post.all() # Defaults to every post. (?gplb nsfw, eg.)

		leaderboard = {} # Prepares an empty dictionary.
		j = 0
		for x in result: # For each entry in the database:
			leaderboard[j] = [int(x.get("points")), str(x.get("content")), str(x.get("username")), str(x.get("embed")), str(x.get("servers")), str(x.get("stars")), str(x.get("nsfw")), str(x.get("richembed"))] # ...save the user's ID and its amount of points in a new Python database.
			j = j+1
		
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1][0], reverse=True)

		page = 1

		await printLeaderboard(page, leaderboard, self, ctx, ctx.message, ctx, args, True)

	# ---------------------------------
	#	    ?PLB (SERVER POST LB)
	# ---------------------------------
	
	@commands.command(aliases=['splb', 'plb', 'serverpostleaderboard', 'postleaderboards', 'serverpostleaderboards'], description="Check the top 10 posts of all time on this server! May take a while to load. By default, it shows all comments regardless if they were posted in Not Safe for Work channels or not - ?plb nsfw will let you see NSFW posts only, and ?plb sfw will let you see only SFW posts.")
	async def postleaderboard(self, ctx, *args):
		"""Shows posts with most karma on this server!"""
		currentguild = str(ctx.message.guild.id)
		User = Query()

		if not args:
			result = post.search(Query()['servers'] == currentguild) # "Result" is just the entire database.
		else:
			if ctx.message.mentions:
				valor = str(ctx.message.mentions[0].id)
				print(valor)
				result = post.search((User.servers == currentguild) & (User.username == valor))
			else:
				result = post.search(Query()['servers'] == currentguild) # Defaults to every post. (?plb sfw, eg.)

		leaderboard = {} # Prepares an empty dictionary.
		j = 0
		for x in result: # For each entry in the database:
			leaderboard[j] = [int(x.get("points")), str(x.get("content")), str(x.get("username")), str(x.get("embed")), str(x.get("servers")), str(x.get("stars")), str(x.get("nsfw")), str(x.get("richembed"))] # ...save the user's ID and its amount of points in a new Python database.
			j = j+1
		
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1][0], reverse=True)

		page = 1
		
		await printLeaderboard(page, leaderboard, self, ctx, ctx.message, ctx, args, False)


# -------------------------------
# 	  LEADERBOARD FUNCTIONS
# -------------------------------


def setup(client):
	client.add_cog(Karma(client))
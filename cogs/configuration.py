# Import global variables and databases.
from definitions import srv, best, customprefix, chan, botname, support

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

# sharedFunctions
from sharedFunctions import printLeaderboard, createLeaderboardEmbed, getProfile, sendErrorEmbed, getCurrentPrefix

# ----------------------------------------------------------------------------------------------

class Configuration(commands.Cog):
	"""
	Things that have to do with setting up and personalizing the bot.
	"""
	def __init__(self, client):
		self.client = client
	
	# ---------------------
	#	  SET UP BOT
	# ---------------------
	
	@commands.command(name="setup", pass_context=True, description="Sets up the bot, creating the necessary roles, channels and emojis for it to function. REQUIRED ROLES: Manage messages")
	@commands.has_permissions(manage_guild=True)
	async def setup(self, ctx):
		"""Sets up the bot automagically. REQUIRED ROLES: Manage messages"""
		loadingEmoji = self.client.get_emoji(660250625107296256)
		loadingText = await ctx.send(str(loadingEmoji) + " Getting " + botname + " ready to go...")
		error = False
		creationLog = ""
		prefix = await getCurrentPrefix(ctx)

		# Register server in database!
		# This should be unnecessary unless it's a VERY specific, debug-y case.
		srv.upsert({'serverid': ctx.guild.id, 'heart': 'plus', 'crush': 'minus', 'star': '10', 'global': True}, Query().serverid == ctx.guild.id)
		
		# If the role "Curator" doesn't exist, the bot creates it.
		try:
			rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
			if rolesearch == None:
				await ctx.guild.create_role(name="Curator")
				creationLog += "\n- The Curator role (users with this role can use the Star emoji) was created."
		except Exception as e:
			error = True
			errorLog = "Something happened while creating the role *Curator*. Maybe the bot doesn't have sufficient permissions?"
		
		# If the channel "#best-of" doesn't exist, the bot creates it.
		try:
			channelsearch = discord.utils.get(ctx.guild.channels, name="best-of")
			if channelsearch == None:
				server = str(ctx.message.guild.id)
				await ctx.guild.create_text_channel('best-of')
				channelid = discord.utils.get(self.client.get_all_channels(), name='best-of')
				print(channelid.id)
				best.upsert({'serverid': server, 'channelid': channelid.id, 'notification': "message"}, Query().serverid == server)
				creationLog += "\n- The Best Of channel, where Starred comments lie, was created."
		except Exception as e:
			error = True
			errorLog = "There was an error while trying to create the Best Of channel. May have to do with permissions?"

		# If the user who executed the command doesn't have assigned the role "Curator", the bot assigns it.
		try:
			if discord.utils.get(ctx.message.author.roles, name="Curator") is None:
				role = discord.utils.get(ctx.guild.roles, name="Curator")
				await ctx.message.author.add_roles(role)
				creationLog += "\n- You were given the role Curator."
		except Exception as e:
			error = True
			errorLog = "While creating the role Curator, an error occurred. May have to do something with permissions."

		# If the emoji "10" doesn't exist, the bot creates it.
		try:
			rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
			emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
			if emojisearch == None:
				with open("images/star.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
					creationLog += "\n- The emoji Star (+10) was created. Only Curators can use it to add content to the Best Of channel!"
		except Exception as e:
			error = True
			errorLog = "Trying to create the role-exclusive emoji Star (10) sent out an error. Maybe there's not enough space for new emoji, or the bot doesn't have permissions."

		# If the emoji "plus" doesn't exist, the bot creates it.
		try:
			plussearch = discord.utils.get(ctx.guild.emojis, name="plus")
			if plussearch == None:
				with open("images/plus.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="plus", image=image.read())
					creationLog += "\n The emoji Heart (+1) was created."
		except Exception as e:
			error = True
			errorLog = "Trying to create the emoji Heart (plus) sent out an error. Maybe there's not enough space for new emoji, or the bot doesn't have permissions."
		
		# If the emoji "minus" doesn't exist, the bot creates it.
		try:
			minussearch = discord.utils.get(ctx.guild.emojis, name="minus")
			if minussearch == None:
				with open("images/minus.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="minus", image=image.read())
					creationLog += "\n- The emoji Crush (-1) was created."
		except Exception as e:
			error = True
			errorLog = "Trying to create the emoji Crush (minus) sent out an error. Maybe there's not enough space for new emoji, or the bot doesn't have permissions."
		
		await loadingText.delete()
		emoji = discord.utils.get(ctx.message.guild.emojis, name="10")
		
		if error == False and creationLog != "":
			await ctx.send("**" + botname + "** is now set up and ready to go!\n\n*What changed?*")
			creationLog += "\n"
			if creationLog != "":
				await ctx.send(creationLog)
			await ctx.send("*What now?*\n- Giving someone the role *Curator* on Server Settings will let them use the " + str(emoji) + " emoji to star posts. A Discord restart (CTRL+R) may be needed to see the emoji.\n- Edit the look of the default emojis using the command " + prefix + "emoji to make " + botname + " your own!\n- Rename the #best-of channel to a name you like the most on Server Settings.\n- Use the command " + prefix + "notification if your server is big, and you'd rather change the confirm message (e.g. Congrats! +10 points to the user) to a reaction.")
			if support != "":
				await ctx.send("- If any issues arise, make sure to check in on " + botname + "'s official support server, over at **" + support + "**. :heart:")
			else:
				await ctx.send("- Thank you very much for installing **" + botname + "**! :heart:")
		elif error == True:
			await sendErrorEmbed(ctx, "Something happened and the setup couldn't be completed. (" + errorLog + ")\n- Check that there is space to create three new emojis and that the bot has sufficient permissions.\n- If you're certain everything was taken care of, try running the setup command again.")
		else:
			await ctx.send("**" + botname + "** was already set up - nothing has changed!\n\n*Want some pointers?*\n- Giving someone the role *Curator* on Server Settings will let them use the " + str(emoji) + " emoji to star posts. A Discord restart (CTRL+R) may be needed to see the emoji.\n- Edit the look of the default emojis using the command " + prefix + "emoji to make " + botname + " your own!\n- Rename the #best-of channel to a name you like the most on Server Settings.\n- Use the command " + prefix + "notification if your server is big, and you'd rather change the confirm message (e.g. Congrats! +10 points to the user) to a reaction.")
			if support != "":
				await ctx.send("- If any issues arise, make sure to check in on " + botname + "'s official support server, over at **" + support + "**. :heart:")
			else:
				await ctx.send("- Thank you very much for installing **" + botname + "**! :heart:")
			
			
	# -------------------------
	#		MANAGE EMOJIS
	# -------------------------
				
	@commands.command(aliases=['reto', 'config', 'cfg', 'emojis', 'settings'], description='Used by server admins to manage their emojis. ?emoji edit to change the look of a heart/crush/10 points, ?emoji default to restore all emojis, ?emoji best-of to change the name of #best-of. REQUIRED ROLES: Manage messages')
	@commands.has_permissions(manage_guild=True)
	async def emoji(self, ctx, *args):
		"""Used to manage bot emojis. REQUIRED ROLES: Manage messages"""
		script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
		rel_path = "../images/testimage.png"
		path = os.path.join(script_dir, rel_path)
		prefix = await getCurrentPrefix(ctx)
		if not args:
			await ctx.send("Please provide an argument!\n**" + prefix + "emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**" + prefix + "emoji default** - Restores the custom emoji (10/plus/minus) to their original state.\n**" + prefix + "emoji best-of** - Allows you to rename the Best Of channel for personalization!")
		elif args[0] == "best-of":
			if not args[1]:
				await sendErrorEmbed(ctx, "No name for the #best-of channel was provided. Usage: " + prefix + "emoji best-of Channel-For-Cool-Posts")
			else:
				server = str(ctx.message.guild.id)
				best.upsert({'serverid': server, 'name': args[1]}, Query().serverid == server)
				await ctx.send("The best-of channel hath now been renamed to " + args[1] + "!")
		elif args[0] == "edit":
			if len(args) != 2:
				await sendErrorEmbed(ctx, "No emoji name was provided. Valid emoji names: 10/plus/minus")
			elif args[1] == "10":
					if not ctx.message.attachments:
						await sendErrorEmbed(ctx, "Couldn't find an image! Upload an image along with your command (not an URL).")
					else:
						async with aiohttp.ClientSession() as session:
							url = ctx.message.attachments[0].url
							print (url)
							async with session.get(url) as resp:
								if resp.status == 200:
									f = await aiofiles.open(path, mode='wb')
									await f.write(await resp.read())
									await f.close()
									rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
									with open("images/testimage.png", "rb") as image:
										emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
										await emojisearch.delete()
										await ctx.guild.create_custom_emoji(name="10", image=image.read())
										await ctx.send("The emoji **:10:** has been modified.")
										
			elif args[1] == "plus":
					if not ctx.message.attachments:
						await sendErrorEmbed(ctx, "Couldn't find an image! Upload an image along with your command (not an URL).")
					else:
						async with aiohttp.ClientSession() as session:
							url = ctx.message.attachments[0].url
							print (url)
							async with session.get(url) as resp:
								if resp.status == 200:
									f = await aiofiles.open(path, mode='wb')
									await f.write(await resp.read())
									await f.close()
									rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
									with open("images/testimage.png", "rb") as image:
										emojisearch = discord.utils.get(ctx.guild.emojis, name="plus")
										await emojisearch.delete()
										await ctx.guild.create_custom_emoji(name="plus", image=image.read())
										await ctx.send("The emoji **:plus:** has been modified.")
			elif args[1] == "minus":
					if not ctx.message.attachments:
						await sendErrorEmbed(ctx, "Couldn't find an image! Upload an image along with your command (not an URL).")
					else:
						async with aiohttp.ClientSession() as session:
							url = ctx.message.attachments[0].url
							print (url)
							async with session.get(url) as resp:
								if resp.status == 200:
									f = await aiofiles.open(path, mode='wb')
									await f.write(await resp.read())
									await f.close()
									rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
									with open("images/testimage.png", "rb") as image:
										emojisearch = discord.utils.get(ctx.guild.emojis, name="minus")
										await emojisearch.delete()
										await ctx.guild.create_custom_emoji(name="minus", image=image.read())
										await ctx.send("The emoji **:minus:** has been modified.")
			else:
				await sendErrorEmbed(ctx, "Invalid emoji name. Valid names: 10/plus/minus")
		elif args[0] == "default":
			try:
				# Restore :10:
				rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
				emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
				if emojisearch == None:
					with open("images/star.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
				else:
					await emojisearch.delete()
					with open("images/star.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
				# Restore :plus:
				emojisearch = discord.utils.get(ctx.guild.emojis, name="plus")
				if emojisearch == None:
					with open("images/plus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="plus", image=image.read())
				else:
					await emojisearch.delete()
					with open("images/plus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="plus", image=image.read())
				# Restore :minus:
				emojisearch = discord.utils.get(ctx.guild.emojis, name="minus")
				if emojisearch == None:
					with open("images/minus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="minus", image=image.read())
				else:
					await emojisearch.delete()
					with open("images/minus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="minus", image=image.read())
				await ctx.send("All emojis have been restored!")
			except:
				await sendErrorEmbed(ctx, "An error has occurred while restoring the emojis. Check the bot's permissions and that there's space for three more emojis and try again!")
		else:
			await ctx.send("Invalid argument!\n**" + prefix + "emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**" + prefix + "emoji default** - Restores the custom emoji (10/plus/minus) to their original state.\n**" + prefix + "emoji best-of** - Allows you to rename the Best Of channel for personalization!")

	# -------------------------
	#	SET UP NAME MODIFYING
	# -------------------------
				
	@commands.command(description="Let's get you set up and ready to change #best-of's name with this command!")
	@commands.has_permissions(manage_guild=True)
	async def name(self,ctx,*args):
		"""Get the ability to change #best-of's name!"""
		y2k = await ctx.send(":arrows_counterclockwise: Looking up if you're set up already...")
		best.clear_cache()
		server = str(ctx.message.guild.id)
		channel = best.search(Query().serverid == server)
		if (channel):
			await ctx.send(":white_check_mark: **You're already set up!**")
			await ctx.send("If you want to change the name of the #best-of channel, you can edit it on the Discord settings as usual!")
			await y2k.delete()
		else:
			channelid = discord.utils.get(self.client.get_all_channels(), name='best-of')
			print(channelid.id)
			best.upsert({'serverid': server, 'channelid': channelid.id, 'notification': "message"}, Query().serverid == server)
			await ctx.send(":raised_hands: **You weren't set up**, so I did it for you.")
			await ctx.send("If you want to change the name of the #best-of channel, you can edit it on the Discord settings as usual!")
			await y2k.delete()

	# -------------------------
	#	  CHANGE BOT PREFIX
	# -------------------------
				
	@commands.command(description="Change the bot's prefix to whichever you want. You can also use ?prefix default to get everything back to normal.")
	@commands.has_permissions(manage_guild=True)
	async def prefix(self,ctx,*args):
		"""Change the bot's prefix to whichever you want."""

		prefix = await getCurrentPrefix(ctx)
		if args:
			if args[0] == "default":
				pre = customprefix.get(Query().server == ctx.message.guild.id)
				customprefix.remove(doc_ids=[int(pre.doc_id)])
				await ctx.send("Your prefix is back to normal! You can now use `?` on " + botname + "'s commands.")
			else:
				customprefix.upsert({'server': ctx.message.guild.id, 'prefix': args[0]}, Query().server == ctx.message.guild.id)
				await ctx.send("Your prefix is now `" + args[0] + "`! You can now use it as a prefix to " + botname + "'s commands.")
		else:		 
			await ctx.send("Set up your prefix by writing in `" + prefix + "prefix *symbol*`. If you've messed up, you can restore it to default by writing `" + prefix + "prefix default`.\n_(Bot prompts will accomodate to this new prefix, except for the command descriptions on " + prefix + "help.)._")


	# -------------------------
	#	 ENABLE AUTO-VOTES
	# -------------------------
				
	@commands.command(aliases=['autovotes', 'autoreact', 'autoreacts', 'autoreactions'], description="Enable/disable the bot reacting to every message in a certain channel! This is useful for image channels, where you'd want to have every post already reacted to with a Heart and a Crush to encourage voting. (You can also enable this server-wide, with ?autovote server.)")
	@commands.has_permissions(manage_guild=True)
	async def autovote(self,ctx,*args):
		"""Enable/disable the bot reacting to every message in a channel!"""

		prefix = await getCurrentPrefix(ctx)
		if args:
			if args[0] == "server":
				# Check if the channel exists.
				result = chan.get(Query()['server'] == ctx.message.guild.id)
				if (result and result['serverwide'] == True):
					await ctx.send("The Autovote feature has been disabled server-wide. This does not affect channels that already have Autovote enabled - those need to be disabled manually.\nTo enable it, use " + prefix + "autovote server again.")
					chan.update({'serverwide': False}, where('server') == ctx.message.guild.id)
				else:
					await ctx.send("The Autovote feature has been enabled server-wide! To disable it, use " + prefix + "autovote server again.")
					exists = chan.count(Query().server == ctx.message.guild.id)
					if (exists == 0):
						chan.insert({'server': ctx.message.guild.id, 'channels': [], 'serverwide': True})
					else:
						chan.update({'serverwide': True}, where('server') == ctx.message.guild.id)
		else:
			# Check if the channel exists.
			result = chan.get(Query()['server'] == ctx.message.guild.id)
			if (result and ctx.message.channel.id in result['channels']):
				await ctx.send("The Autovote feature has been disabled on **#" + ctx.message.channel.name + "** successfully.\nTo re-enable this feature, use " + prefix + "autovote on this channel again.")
				newresult = result['channels']
				newresult.remove(ctx.message.channel.id)
				chan.update({'channels': newresult}, where('server') == ctx.message.guild.id)
			else:
				plus = discord.utils.get(ctx.message.guild.emojis, name="plus")
				minus = discord.utils.get(ctx.message.guild.emojis, name="minus")
				await ctx.send("The Autovote feature has been enabled on the channel **#" + ctx.message.channel.name + "**! From now on, every post in this channel will be auto-reacted to with " + str(plus) + " and " + str(minus) + ", to encourage voting.\nTo disable this feature, use " + prefix + "autovote on this channel again.")
				exists = chan.count(Query().server == ctx.message.guild.id)
				if (exists == 0):
					chan.insert({'server': ctx.message.guild.id, 'channels': [], 'serverwide': False})
				chan.update(add('channels',[ctx.message.channel.id]), where('server') == ctx.message.guild.id)

	# -------------------------
	#	CHANGE NOTIFICATIONS
	# -------------------------
				
	@commands.command(aliases=['notif', 'notifications'], description="Change the confirm notification settings (e.g. Congrats! X person gave you a star and now you're in the Best Of channel.) from Reactions to Messages. (?notification message/?notification reaction)")
	@commands.has_permissions(manage_guild=True)
	async def notification(self,ctx,*args):

		prefix = await getCurrentPrefix(ctx)
		"""Change confirm notif. to messages or reactions."""
		loadingEmoji = self.client.get_emoji(660250625107296256)
		okayEmoji = self.client.get_emoji(660217963911184384)
		server = str(ctx.message.guild.id)
		best.clear_cache()
		server = str(ctx.message.guild.id)
		channel = best.search(Query().serverid == server)
		if not channel:
			channelid = discord.utils.get(self.client.get_all_channels(), name='best-of')
			best.upsert({'serverid': server, 'channelid': channelid.id, 'notification': "message"}, Query().serverid == server)
		notifmode = best.search(Query().serverid == server)
		notifmode = notifmode[0]['notification']
		notifstr = str(notifmode)
		if not args:
			await ctx.send("You're currently using **" + notifstr.capitalize() + "** Mode.\n💠 *" + prefix + "notification message* tells " + botname + " to send a message when someone Stars/Hearts/Crushes a comment. Great for small servers, and shows the Karma that the user currently has.\n💠 *" + prefix + "notification reaction* sends a reaction when someone Stars/Hearts/Crushes a comment. Great if you don't want to have excess notifications on Mobile, but it doesn't show the Karma the user has.\n💠 *" + prefix + "notification disabled* deactivates notifications on this server - no messages or reactions when someone Stars/Hearts/Crushes a comment. This isn't recommended unless it's being used in a very heavy server, as it leaves zero feedback that their vote has been counted.")
		elif args[0] == "reaction" or args[0] == "reactions":
			best.update({"notification": "reaction"}, where('serverid') == server)
			await ctx.send("*Got it!* The server will send confirmations as a reaction.\nNext time someone reacts to a comment, said message will be reacted with " + str(okayEmoji) + " for a couple of seconds.")
		elif args[0] == "message" or args[0] == "messages":
			best.update({"notification": "message"}, where('serverid') == server)
			await ctx.send("*Got it!* The server will send confirmations as messages.\nNext time someone reacts to a comment, they'll be sent a message as confirmation (which will delete itself after a couple of seconds).")
		elif args[0] == "disabled":
			best.update({"notification": "disabled"}, where('serverid') == server)
			await ctx.send("*Got it!* The server will not send confirmations.\nNext time someone reacts to a comment, it will be counted, but there'll be no confirmation of it.")
		else:
			await sendErrorEmbed(ctx, "That's not a valid option!")
		

def setup(client):
	client.add_cog(Configuration(client))
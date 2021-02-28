from definitions import support, botowner, prefix, debug, db, srv, post, dm, best, priv, customprefix

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
import ast

# ----------------------------------------------------------------------------------------------

async def getCurrentPrefix(ctx):
	customprefix.clear_cache()
	if not ctx.message.guild: # is on DMs
		return prefix
	else:
		pre = customprefix.search(Query().server == ctx.guild.id)
		if pre:
			return pre[0]['prefix']
		else:
			return prefix

async def getProfile(author, ctx, self):
	valor = str(author)
	searchvalor = str(author.id)

	result = db.get(Query()['username'] == searchvalor)

	#
	# CONSEGUIR VALOR EN LA GLB
	#

	if not isinstance(ctx.message.channel, discord.channel.DMChannel):
		server = str(ctx.message.guild.id)
	db.clear_cache()
	lbsult = db.all() # doesnt work
	leaderboard = {} # Prepares an empty dictionary.
	for x in lbsult: # For each entry in the database:
		leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
	leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
	s = ""
	leadervalue = 1

	for key, value in leaderboard: # For each value in the new, sorted DB:
		if key == searchvalor:
			break
		else:
			leadervalue += 1

	#
	# CONSEGUIR VALOR EN LA LLB
	#

	if not isinstance(ctx.message.channel, discord.channel.DMChannel):
		llbsult = db.search(Query().servers.all([server])) # doesnt work
		lleaderboard = {} # Prepares an empty dictionary.
		for x in llbsult: # For each entry in the database:
			lleaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		lleaderboard = sorted(lleaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		s = ""
		localvalue = 1

		for key, value in lleaderboard: # For each value in the new, sorted DB:
			if key == searchvalor:
				break
			else:
				localvalue += 1

	#
	# GLB BADGE
	#

	if result:
		if leadervalue == 1:
			leaderemblem = "🥇"
		elif leadervalue == 2:
			leaderemblem = "🥈"
		elif leadervalue == 3:
			leaderemblem = "🥉"
		elif leadervalue <= 10:
			leaderemblem = "🏅"
		else:
			leaderemblem = " "
	else:
		leaderemblem = " "

	#
	# REVISAR ESTATUS DE CURATOR
	#

	curatoremblem = ""
	if not isinstance(ctx.message.channel, discord.channel.DMChannel):
		curatoremote = self.client.get_emoji(742136325628756000)
		role = discord.utils.get(ctx.guild.roles, name="Curator")
		if role in author.roles:
			curatoremblem = str(curatoremote)

	#
	# REVISAR ESTATUS DE BOTOWNER
	#

	botemblem = ""
	for x in botowner:
		if (int(author.id) == int(x)):
			botemblem = "👨‍💻"

	#
	# POINTS SENT
	#

	sentpoints = post.search(Query().voters.any([author.id]))

	#
	# STARS RECEIVED
	#

	starlist = post.search(Query().username == str(author.id))
	starsrec = 0
	for star in starlist:
		if 'stars' in star:
			starsrec += star['stars']

	#
	# SUPPORT BADGES (WIP)
	#

	#checkM = self.client.get_emoji(741669341409312889)
	#print(str(checkM))

	#
	# SEND THE EMBED
	#

	embed=discord.Embed(title=author.name + ' ' + leaderemblem + str(curatoremblem) + botemblem)
	embed.set_thumbnail(url=author.avatar_url)
	if result:
		embed.add_field(name="Karma", value=result.get('points'), inline=True)
	else:
		embed.add_field(name="Karma", value='0', inline=True)
	if result:
		embed.add_field(name="Global Rank", value=leadervalue, inline=True)
		if not isinstance(ctx.message.channel, discord.channel.DMChannel):
			embed.add_field(name="Local Rank", value=localvalue, inline=True)
		embed.add_field(name="Reacted posts", value=len(sentpoints), inline=True)
		embed.add_field(name="Stars received", value=starsrec, inline=True)
	await ctx.send(embed=embed)

#####

async def printLeaderboard(page, leaderboard, self, ctx, ctxMessage, ctxChannel, args, isGlobal):
	numero = ((page-1) * 5) + 1
	ceronumero = 1
	lbEmbed = [None] * 12
	embedIds = [None] * 12
	typeArgs = 'default'

	hardLimit = 6 #maximum amount of pages you can show on ?gplb. default is 6 (up to 25 messages)

	if len(leaderboard) == 0:
		await sendErrorEmbed(ctxChannel, "Looks like this leaderboard is empty! Why don't we get started by reacting to posts?")
		await ctxMessage.remove_reaction(checkM, botid)

	elif (isGlobal == True and not page > hardLimit) or isGlobal == False: 
		if ctxMessage:
			checkM = self.client.get_emoji(660250625107296256)
			react = await ctxMessage.add_reaction(checkM)
		
		for key,values in leaderboard[(numero-1):]:
			srvSettings = srv.search(Query().serverid == int(values[4]))[0]
			if (isGlobal == True and (("global" in srvSettings and srvSettings['global'] == True) or (not "global" in srvSettings))) or (isGlobal == False):
				if numero != ((page * 5) + 1):
					if args:
						if args[0] == "nsfw":
							if (values[6] == "True"):
								typeArgs = 'nsfw'
								lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
								if lbEmbed[ceronumero]:
									embedIds[ceronumero] = lbEmbed[ceronumero].id
								numero = numero + 1
								ceronumero = ceronumero + 1
						elif args[0] == "sfw" and isGlobal == False:
							if (values[6] != "True" or values[6] == "None"):
								typeArgs = 'sfw'
								lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
								if lbEmbed[ceronumero]:
									embedIds[ceronumero] = lbEmbed[ceronumero].id
								numero = numero + 1
								ceronumero = ceronumero + 1

						elif args[0] == "all" and isGlobal == True:
							typeArgs = 'all'
							lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
							if lbEmbed[ceronumero]:
								embedIds[ceronumero] = lbEmbed[ceronumero].id
							numero = numero + 1
							ceronumero = ceronumero + 1
						else:
							print("Oh no.")
							typeArgs = 'mention'
							lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
							if lbEmbed[ceronumero]:
								embedIds[ceronumero] = lbEmbed[ceronumero].id
							numero = numero + 1
							ceronumero = ceronumero + 1
					else:
						if isGlobal == False:
							typeArgs = 'default'
							lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
							if lbEmbed[ceronumero]:
								embedIds[ceronumero] = lbEmbed[ceronumero].id
							numero = numero + 1
							ceronumero = ceronumero + 1
						elif values[6] != "True" or values[6] == "None":
							typeArgs = 'default'
							lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
							if lbEmbed[ceronumero]:
								embedIds[ceronumero] = lbEmbed[ceronumero].id
							numero = numero + 1
							ceronumero = ceronumero + 1
			else:
				print("Este valor fue ocultado por Server Logging!")

		if any(lbEmbed):
			cleanIds = list(filter(None, embedIds))
			if (lbEmbed[(int(ceronumero)-1)] == False): 
				lbEmbed[(int(ceronumero)-1)] = lbEmbed[(int(ceronumero)-2)]
			remove = await lbEmbed[(int(ceronumero)-1)].add_reaction("🗑️")
			if page > 1:
				nextitem = await lbEmbed[(int(ceronumero)-1)].add_reaction("⬅️")
			if (numero) == ((page * 5) + 1) and (page != hardLimit - 1 or isGlobal == False):
				if (len(leaderboard) >= numero):
					nextitem = await lbEmbed[(int(ceronumero)-1)].add_reaction("➡️")

			dm.insert({'id': lbEmbed[(int(ceronumero)-1)].id, 'messages': cleanIds, 'type': typeArgs, 'page': page, 'global': isGlobal})
		else:
			await sendErrorEmbed(ctxChannel, "The leaderboard didn't generate itself correctly. This should happen either if no one has ever voted on a post (if you just installed Reto, for example), or if Reto has no access to any of the servers where the top posters are. (Using real databases in test bots, maybe?)")
		botid = self.client.user
		await ctxMessage.remove_reaction(checkM, botid)

async def createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page):

	emoji = discord.utils.get(ctxMessage.guild.emojis, name="plus")
	guild = ctxMessage.guild

	username = self.client.get_user(int(values[2]))
	guild = self.client.get_guild(int(values[4]))
	if username and guild:
		contenido=values[1]
		autor=username
		foto=username.avatar_url
		if(len(values[3]) > 0):
			imagen=values[3]

		if numero == 1:
			emberino=discord.Embed(description=contenido, colour=discord.Colour(0xffd700))
		elif numero == 2:
			emberino=discord.Embed(description=contenido, colour=discord.Colour(0xc0c0c0))
		elif numero == 3:
			emberino=discord.Embed(description=contenido, colour=discord.Colour(0xcd7f32))
		else:
			emberino=discord.Embed(description=contenido, colour=discord.Colour(0xa353a9))
		
		# the user may not have a profile pic!
		if (foto):
			emberino.set_author(name=autor, icon_url=foto)
		else:
			emberino.set_author(name=autor)

		# the server may not have an icon!
		if (guild.icon_url):
			emberino.set_footer(text=guild, icon_url=guild.icon_url)
		else:
			emberino.set_footer(text=guild)

		# Parsing embeds:

		if values[7]:
			for embed in ast.literal_eval(values[7]):
				thisEmbed = emberino.to_dict()
				if not (len(values[3]) > 0) and not "image" in thisEmbed:
					if "thumbnail" in embed:
						emberino.set_image(url=embed['thumbnail']['url'])
					if "image" in embed:
						emberino.set_image(url=embed['image']['url'])
				title = ""
				description = ""
				if "title" in embed:
					title = embed['title']
				elif "author" in embed:
					title = embed['author']['name']
				if "description" in embed:
					description = embed['description']
				if title and description:
					emberino.add_field(name=title, value=description, inline=False)
				if "fields" in embed:
					for field in embed["fields"]:
						emberino.add_field(name=field['name'], value=field['value'], inline=False)

		if numero == 1:
			emberino.add_field(name="Position", value="🥇 "+str(numero), inline=True)
		elif numero == 2:
			emberino.add_field(name="Position", value="🥈 "+str(numero), inline=True)
		elif numero == 3:
			emberino.add_field(name="Position", value="🥉 "+str(numero), inline=True)
		else:
			emberino.add_field(name="Position", value="✨ "+str(numero), inline=True)
		emberino.add_field(name="Karma", value=f"{emoji} " + str(values[0]), inline=True)
		if (values[5] != "None"): #if theres 'stars' value in post
			emberino.add_field(name="Stars", value=":star2: "+str(values[5]), inline=True)
		if(len(values[3]) > 0):
			emberino.set_image(url=values[3])

		if numero != ((page * 5) + 1):
			lbEmbed[ceronumero] = await ctxChannel.send(embed=emberino)
		else:
			lbEmbed[ceronumero] = False
		return lbEmbed[ceronumero]

async def sendErrorEmbed(ctxChannel, description):
	title = "Looks like something went wrong..."
	if random.randint(0,100) == 69:
		title = "Oopsie Woopsie! UwU. We made a fuggy wuggy!!"
	embed=discord.Embed(title=title, description=description, color=0xfe2c2c)
	embed.set_footer(text="Need help? Reach us at our support server! " + support)
	await ctxChannel.send(embed=embed)

# TO-DO: Optimize.
# This is RAW, man.

async def reactionAdded(bot, payload):
	if payload.guild_id is None:
		return
	User = Query()
	userid  = payload.user_id
	# Misc. definitions.
	# Attempt a get_x command for brevity. If that doesn't work, use fetch_x (slow).
	user = bot.get_user(payload.user_id)
	if not user:
		user = await bot.fetch_user(payload.user_id)
		print("User not found. Trying to fetch it...")
	channel = bot.get_channel(payload.channel_id)
	if not channel:
		channel = await bot.fetch_channel(payload.channel_id)
		print("Channel not found. Trying to fetch it...")
	guild = bot.get_guild(payload.guild_id)
	if not guild:
		guild = await bot.fetch_guild(payload.guild_id)
		print("Guild not found. Trying to fetch it...")
	member = guild.get_member(payload.user_id)
	if not member:
		member = await guild.fetch_member(payload.user_id)
		print("Member not found. Trying to fetch it...")
	# no such thing as "get_message"
	message = await channel.fetch_message(payload.message_id)

	if ((userid != message.author.id) or (debug == True)) and not user.bot:
		if not isinstance(payload.emoji, str):
			# -------------------------
			#	  REACTION = :10:
			# -------------------------
			
			channel = message.channel
			is_nsfw = channel.is_nsfw()
			
			if payload.emoji.name == '10':
				if discord.utils.get(member.roles, name="Curator") is None:
					await message.remove_reaction(payload.emoji, user)
				else:
					channel = message.channel
					
					messageurl = "https://discordapp.com/channels/" + str(message.guild.id) + "/" + str(message.channel.id) + "/" + str(message.id)
					
					# Post the message in #best-of

					contenido=message.content
					autor=message.author.name
					foto=message.author.avatar_url
					if(len(message.attachments) > 0):
						imagen=message.attachments[0].url

					color = ""

					# If there's an embed, set the color of the new embed to it. (first come, first serve)

					if (message.embeds):
						embed = message.embeds[0].to_dict()
						if "color" in embed:
							color = embed['color']
					if color:
						emberino=discord.Embed(description=contenido, color=color)
					else:
						emberino=discord.Embed(description=contenido)

					emberino.set_author(name=autor, url=messageurl, icon_url=foto)
					if(len(message.attachments) > 0):
						emberino.set_image(url=imagen)

					# Parsing embeds:

					if (message.embeds):
						for embed in message.embeds:
							embed = embed.to_dict()
							thisEmbed = emberino.to_dict()
							if (len(message.attachments) == 0) and not "image" in thisEmbed:
								if "thumbnail" in embed:
									emberino.set_image(url=embed['thumbnail']['url'])
								if "image" in embed:
									emberino.set_image(url=embed['image']['url'])
							if not "footer" in thisEmbed:
								if "footer" in embed:
									emberino.set_footer(text=embed['footer']['text'])
								else:
									footer = ""
									if "provider" in embed:
										footer = embed['provider']['name']
									if "author" in embed and not "title" in embed:
										footer = embed['author']['name']
									if footer:
										emberino.set_footer(text=footer)
							title = ""
							description = ""
							if "title" in embed:
								title = embed['title']
							elif "author" in embed:
								title = embed['author']['name']
							if "description" in embed:
								description = embed['description']
							if title and description:
								emberino.add_field(name=title, value=description, inline=False)
							if "fields" in embed:
								for field in embed["fields"]:
									emberino.add_field(name=field['name'], value=field['value'], inline=False)

					# the difficult challenge of finding the channel to post to
					
					best.clear_cache()
					server = str(message.guild.id)
					channel = best.search(Query().serverid == server)

					valuetwo = str(message.id)

					postexists = post.search(Query().msgid == valuetwo)
					if postexists:
						postexists = int(postexists[0]['stars'])
					else:
						postexists = 0

					if (postexists == 0):
						try:
							channel = channel[0]['channelid'] # channel id of best-of channel
							channel = discord.utils.get(message.guild.channels, id=channel)
							if channel == None:
								channel = discord.utils.get(message.guild.channels, name="best-of")
								if channel == None:
									# if the bot doesn't find a channel named best-of, the channnel has been deleted. create a new one!
									await message.guild.create_text_channel('best-of')
									channel = discord.utils.get(message.guild.channels, name="best-of")
									best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
									channelformsg = message.channel
									await channelformsg.send("The *Best Of* channel doesn't exist, if the bot has permissions it has been created.")
									channel = best.search(Query().serverid == server)
									channel = channel[0]['channelid']
									channel = discord.utils.get(message.guild.channels, id=channel)
								else:
									# if the bot does find a channel named best-of, the channel needs to be linked to the new db.
									# this is for legacy users (1.3.5 and below)
									best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
									channel = best.search(Query().serverid == server)
									channel = channel[0]['channelid']
									channel = discord.utils.get(message.guild.channels, id=channel)
						except IndexError:
							channel = discord.utils.get(message.guild.channels, name="best-of")
							if channel == None:
								# if the bot doesn't find a channel named best-of, the channnel has been deleted. create a new one!
								await message.guild.create_text_channel('best-of')
								channel = discord.utils.get(message.guild.channels, name="best-of")
								best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
								channelformsg = message.channel
								await channelformsg.send("The *Best Of* channel doesn't exist, if the bot has permissions it has been created.")
								channel = best.search(Query().serverid == server)
								channel = channel[0]['channelid']
								channel = discord.utils.get(message.guild.channels, id=channel)
							else:
								# if the bot does find a channel named best-of, the channel needs to be linked to the new db.
								# this is for legacy users (1.3.5 and below)
								best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
								channel = best.search(Query().serverid == server)
								channel = channel[0]['channelid']
								channel = discord.utils.get(message.guild.channels, id=channel)
						
					# Add user to the points table
					value = str(message.author.id)
					exists = db.count(Query().username == value)
					server = str(message.guild.id)
					if exists == 0:
						db.insert({'username': value, 'points': 10, 'servers': [server]})
					else:
						User=Query()
						serverid=str(message.guild.id)
						existsserver = db.count((User.servers.any([serverid])) & (User.username == value))				# no funciona
						if existsserver == 0:
							db.update(add('points',10), where('username') == value)
							l = str(db.search((User.username == value)))
							if "servers" not in l:
								docs = db.search(User.username == value)
								for doc in docs:
									doc['servers'] = [str(server)]
								db.write_back(docs)
							else:
								db.update(add('servers',[server]), where('username') == value)
						else:
							db.update(add('points',10), where('username') == value)
					
					# Finally, the bot sends the message to the Best-Of channel.
					
					if channel == None:
						channelformsg = message.channel
						await sendErrorEmbed(channelformsg, "The channel couldn't be sent to the Best Of channel, for some reason. Could you double-check it exists?")
					else:
						if (postexists == 0):
							await channel.send(embed=emberino)

					# Log post for post leaderboard
						
					priv.clear_cache()
					privSettings = priv.search(Query().username == message.author.id)
					if privSettings:
						privSettings = privSettings[0]

					username = str(message.author.id)
					notifmode = best.search(Query().serverid == server)
					notifmode = notifmode[0]['notification']

					# ISO 8601!
					curdate = str(datetime.now())

					if postexists == 0:
						if not privSettings or "mode" in privSettings and privSettings['mode'] == False or not "mode" in privSettings:
							attachments = ""
							if (len(message.attachments) > 0):
								attachments = message.attachments[0].url
							if (message.embeds):
								richembeds = [None]*len(message.embeds)
								i = 0
								for embed in message.embeds:
									richembeds[i] = embed.to_dict()
									i = i + 1
							else:
								richembeds = ""
							post.insert({'msgid': valuetwo, 'username': username, 'points': 10, 'servers': server, 'content': message.content, 'embed': attachments, 'richembed': richembeds, 'voters': [user.id], 'stars': 1, 'nsfw': is_nsfw, 'timestamp': curdate})
						else:
							print("Privacy Mode ENABLED!")
					else:
						post.update(add('points',10), where('msgid') == valuetwo)
						post.update(add('voters',[user.id]), where('msgid') == valuetwo)
						post.update(add('stars',1), where('msgid') == valuetwo)
						if (notifmode != "reaction") and (notifmode != "disabled"):
							channel = message.channel
							result = db.get(Query()['username'] == value)
							send = await channel.send("Huzzah! **{}**'s post was so good it got starred more than once. They now have {} points. (+10)".format(message.author.name,result.get('points')))
					
					# Send a confirmation message

					channel = message.channel
					result = db.get(Query()['username'] == value)
					
					bestofname = best.search(Query().serverid == server)
					bestofname = bestofname[0]['channelid']
					bestofname = discord.utils.get(message.guild.channels, id=bestofname)

					checkM = bot.get_emoji(660217963911184384)
					if notifmode == "reaction":
						react = await message.add_reaction(checkM)
					if (notifmode != "reaction") and (notifmode != "disabled") and (postexists == 0):
						send = await channel.send("Congrats, **{}**! Your post will be forever immortalized in the **#{}** channel. You now have {} points. (+10)".format(message.author.name,bestofname.name,result.get('points')))
					
					# Delete said message
					if notifmode == "reaction":
						await asyncio.sleep(1) 
						botid = bot.user
						await message.remove_reaction(checkM, botid)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						await asyncio.sleep(3) 
						await send.delete()

			# -------------------------
			#	  REACTION = :PLUS:
			# -------------------------	
			
			if payload.emoji.name == 'plus':
				channel = message.channel

				# Add user to the points table
				value = str(message.author.id)
				exists = db.count(Query().username == value)
				server = str(message.guild.id)
				if exists == 0:
					db.insert({'username': value, 'points': 1, 'servers': [server]})
					# Send a confirmation message or reaction
					notifmode = best.search(Query().serverid == server)
					notifmode = notifmode[0]['notification']
					checkM = bot.get_emoji(660217963911184384)
					if notifmode == "reaction":
						react = await message.add_reaction(checkM)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						result = db.get(Query()['username'] == value)
						heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(message.author.name,result.get('points')))
					if notifmode == "reaction":
						await asyncio.sleep(1) 
						botid = bot.user
						await message.remove_reaction(checkM, botid)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						await asyncio.sleep(3) 
						await heart.delete()
				else:
					User=Query()
					serverid=str(message.guild.id)
					existsserver = db.count((User.servers.any([serverid])) & (User.username == value))				# no funciona
					print(str(existsserver))
					if existsserver == 0:
						db.update(add('points',1), where('username') == value)
						l = str(db.search((User.username == value)))
						print(l)
						if "servers" not in l:
							docs = db.search(User.username == value)
							for doc in docs:
								doc['servers'] = [str(server)]
							db.write_back(docs)
						else:
							db.update(add('servers',[server]), where('username') == value)
					else:
						db.update(add('points',1), where('username') == value)
					
					# Log post for post leaderboard
					
					priv.clear_cache()
					privSettings = priv.search(Query().username == message.author.id)
					if privSettings:
						privSettings = privSettings[0]

					valuetwo = str(message.id)
					username = str(message.author.id)
					postexists = post.count(Query().msgid == valuetwo)

					# ISO 8601!
					curdate = str(datetime.now())
					
					if postexists == 0:
						if not privSettings or "mode" in privSettings and privSettings['mode'] == False or not "mode" in privSettings:
							attachments = ""
							if (len(message.attachments) > 0):
								attachments = message.attachments[0].url
							if (message.embeds):
								richembeds = [None]*len(message.embeds)
								i = 0
								for embed in message.embeds:
									richembeds[i] = embed.to_dict()
									i = i + 1
							else:
								richembeds = ""
							post.insert({'msgid': valuetwo, 'username': username, 'points': 1, 'servers': server, 'content': message.content, 'embed': attachments, 'richembed': richembeds, 'voters': [user.id], 'stars': 0, 'nsfw': is_nsfw, 'timestamp': curdate})
						else:
							print("Privacy Mode ENABLED!")
					else:
						post.update(add('points',1), where('msgid') == valuetwo)
						post.update(add('voters', [user.id]), where('msgid') == valuetwo)

					best.clear_cache()
					notifmode = best.search(Query().serverid == server)
					notifmode = notifmode[0]['notification']
					checkM = bot.get_emoji(660217963911184384)
					if notifmode == "reaction":
						react = await message.add_reaction(checkM)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						result = db.get(Query()['username'] == value)
						heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(message.author.name,result.get('points')))
					
					# Delete said message
					if notifmode == "reaction":
						await asyncio.sleep(1) 
						botid = bot.user
						await message.remove_reaction(checkM, botid)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						await asyncio.sleep(3) 
						await heart.delete()
			
			# -------------------------
			#	  REACTION = :MINUS:
			# -------------------------	
			
			if payload.emoji.name == 'minus':
				channel = message.channel

				# Add user to the points table
				value = str(message.author.id)
				exists = db.count(Query().username == value)
				server = str(message.guild.id)
				if exists == 0:
					db.insert({'username': value, 'points': -1, 'servers': [server]})
					# Send a confirmation message
					notifmode = best.search(Query().serverid == server)
					notifmode = notifmode[0]['notification']
					checkM = bot.get_emoji(660217963911184384)
					if notifmode == "reaction":
						react = await message.add_reaction(checkM)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						result = db.get(Query()['username'] == value)
						crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(message.author.name,result.get('points')))
					if notifmode == "reaction":
						await asyncio.sleep(1) 
						botid = bot.user
						await message.remove_reaction(checkM, botid)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						await asyncio.sleep(3) 
						await crush.delete()


				else:
					User=Query()
					serverid=str(message.guild.id)
					existsserver = db.count((User.servers.any([serverid])) & (User.username == value))				# no funciona
					print(str(existsserver))
					if existsserver == 0:
						db.update(subtract('points',1), where('username') == value)
						l = str(db.search((User.username == value)))
						print(l)
						if "servers" not in l:
							docs = db.search(User.username == value)
							for doc in docs:
								doc['servers'] = [str(server)]
							db.write_back(docs)
						else:
							db.update(add('servers',[server]), where('username') == value)
					else:
						db.update(subtract('points',1), where('username') == value)
					
					# Log post for post leaderboard
					
					priv.clear_cache()
					privSettings = priv.search(Query().username == message.author.id)
					if privSettings:
						privSettings = privSettings[0]

					valuetwo = str(message.id)
					username = str(message.author.id)
					postexists = post.count(Query().msgid == valuetwo)

					# ISO 8601!
					curdate = str(datetime.now())

					if postexists == 0:
						if not privSettings or "mode" in privSettings and privSettings['mode'] == False or not "mode" in privSettings:
							attachments = ""
							if (len(message.attachments) > 0):
								attachments = message.attachments[0].url
							if (message.embeds):
								richembeds = [None]*len(message.embeds)
								i = 0
								for embed in message.embeds:
									richembeds[i] = embed.to_dict()
									i = i + 1
							else:
								richembeds = ""
							post.insert({'msgid': valuetwo, 'username': username, 'points': -1, 'servers': server, 'content': message.content, 'embed': attachments, 'richembed': richembeds, 'voters': [user.id], 'stars': 0, 'nsfw': is_nsfw, 'timestamp': curdate})
						else:
							print("Privacy Mode ENABLED!")
					else:
						post.update(subtract('points',1), where('msgid') == valuetwo)
						post.update(add('voters', [user.id]), where('msgid') == valuetwo)

					# Send a confirmation message
					best.clear_cache()
					notifmode = best.search(Query().serverid == server)
					notifmode = notifmode[0]['notification']
					checkM = bot.get_emoji(660217963911184384)
					if notifmode == "reaction":
						react = await message.add_reaction(checkM)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						result = db.get(Query()['username'] == value)
						crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(message.author.name,result.get('points')))
					
					# Delete said message
					if notifmode == "reaction":
						await asyncio.sleep(1) 
						botid = bot.user
						await message.remove_reaction(checkM, botid)
					if (notifmode != "reaction") and (notifmode != "disabled"):
						await asyncio.sleep(3) 
						await crush.delete()		

async def reactionRemoved(bot, payload):
	if payload.guild_id is None:
		return
	User = Query()
	userid  = payload.user_id

	# Misc. definitions.
	# Attempt a get_x command for brevity. If that doesn't work, use fetch_x (slow).
	user = bot.get_user(payload.user_id)
	if not user:
		user = await bot.fetch_user(payload.user_id)
		print("User not found. Trying to fetch it...")
	channel = bot.get_channel(payload.channel_id)
	if not channel:
		channel = await bot.fetch_channel(payload.channel_id)
		print("Channel not found. Trying to fetch it...")
	guild = bot.get_guild(payload.guild_id)
	if not guild:
		guild = await bot.fetch_guild(payload.guild_id)
		print("Guild not found. Trying to fetch it...")
	member = guild.get_member(payload.user_id)
	if not member:
		member = await guild.fetch_member(payload.user_id)
		print("Member not found. Trying to fetch it...")
	# no such thing as "get_message"
	message = await channel.fetch_message(payload.message_id)

	if ((userid != message.author.id) or (debug == True)) and not user.bot:
		if not isinstance(payload.emoji, str):

			channel = message.channel
			
			removable = None
			if payload.emoji.name == '10':
				# the bot auto-removes stars given out by non-curators.
				# if this is from a non-curator, ignore all this code! otherwise we're just removing points without adding them first.
				if discord.utils.get(member.roles, name="Curator") is None:
					return
				removable = 10
			if payload.emoji.name == 'plus':
				removable = 1
			if payload.emoji.name == 'minus':
				removable = -1

			if removable:
				# Remove the user's karma.
				value = message.author.id
				exists = db.count(Query().username == str(value))
				if not (exists == 0):
					db.update(subtract('points',removable), where('username') == str(value))
				# Remove the comment's karma.
				valuetwo = str(message.id)
				postexists = post.count(Query().msgid == str(valuetwo))
				if not (postexists == 0):
					post.update(subtract('points',removable), where('msgid') == str(valuetwo))
					#post.update(subtract('voters',[user.id]), where('msgid') == str(valuetwo))
					if payload.emoji.name == '10':
						post.update(subtract('stars',1), where('msgid') == str(valuetwo))

				# todo (if possible): remove the message from the best of channel if there are 0 :10: reactions

				# we shouldn't send a message if someone un-reacted, that'd be mean.
				# instead, we send a reaction unless notifications are disabled
				server = str(message.guild.id)
				checkM = bot.get_emoji(660217963911184384)
				notifmode = best.search(Query().serverid == server)
				notifmode = notifmode[0]['notification']
				if notifmode != "disabled":
					react = await message.add_reaction(checkM)
					await asyncio.sleep(1) 
					botid = bot.user
					await message.remove_reaction(checkM, botid)
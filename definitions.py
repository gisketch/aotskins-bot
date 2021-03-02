# New encryption method (1.6)!
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract, delete
from os.path import join as join_path

# Boolean to string parser.
from distutils.util import strtobool

# Unencrypted! This NEEDS to be editable by a simple text editor.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!

for c in cfg:
	bottoken = c['bottoken']
	botname  = c['botname']
	support  = c['support']
	botver   = c['botver']
	prefix   = c['prefix']
	botowner = c['botowner']
	key 	 = c['key']
	debug    = c['debug']
	debug    = bool(strtobool(debug)) # Otherwhise, it's a string.

db           = TinyDB("db/profile.json") #Database file: stores points of every user.
srv          = TinyDB("db/srv.json") #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
activity     = TinyDB("db/activity.json") #Activity file: the "Playing" commands the bot has.
post         = TinyDB("db/post.json") #Comment leaderboard.
priv         = TinyDB("db/priv.json") #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
best         = TinyDB("db/best.json") #Best Of name: Used to look up the Best-Of name of the channel.
dm           = TinyDB("db/dm.json") #Message deletion for Leaderboards.
customprefix = TinyDB("db/customprefix.json") #Prefix file: custom prefixes per server.
chan         = TinyDB("db/chan.json") #Channel file: Used for Autovotes and other channel specific features.
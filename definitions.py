# New encryption method (1.6)!
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract, delete
import tinydb_encrypted_jsonstorage as tae
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

db           = TinyDB(encryption_key=key, path=join_path("db/","profile.reto"), storage=tae.EncryptedJSONStorage) #Database file: stores points of every user.
srv          = TinyDB(encryption_key=key, path=join_path("db/","srv.reto"), storage=tae.EncryptedJSONStorage) #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
activity     = TinyDB(encryption_key=key, path=join_path("db/","activity.reto"), storage=tae.EncryptedJSONStorage) #Activity file: the "Playing" commands the bot has.
post         = TinyDB(encryption_key=key, path=join_path("db/","comments.reto"), storage=tae.EncryptedJSONStorage) #Comment leaderboard.
priv         = TinyDB(encryption_key=key, path=join_path("db/","blacklist.reto"), storage=tae.EncryptedJSONStorage) #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
best         = TinyDB(encryption_key=key, path=join_path("db/","best.reto"), storage=tae.EncryptedJSONStorage) #Best Of name: Used to look up the Best-Of name of the channel.
dm           = TinyDB(encryption_key=key, path=join_path("db/","deletables.reto"), storage=tae.EncryptedJSONStorage) #Message deletion for Leaderboards.
customprefix = TinyDB(encryption_key=key, path=join_path("db/","customprefix.reto"), storage=tae.EncryptedJSONStorage) #Prefix file: custom prefixes per server.
chan         = TinyDB(encryption_key=key, path=join_path("db/","channels.reto"), storage=tae.EncryptedJSONStorage) #Channel file: Used for Autovotes and other channel specific features.
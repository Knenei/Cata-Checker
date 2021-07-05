import os
import asyncio
import discord
import pymongo
import requests
from mojang import MojangAPI
from discord.utils import get
from discord.ext import commands, tasks
from datetime import datetime, timedelta
#from ratelimit import limits, sleep_and_retry


#Version 1.6.0
owner = 418531067008647169
# config (Update as you see fit)
prefix = "%"
#please dont mess with ▽▽▽▽ thanks :)
intents = discord.Intents.default()
intents.members = True 
client = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive = True)
#please dont mess with △△△△ thanks :)
SSB = 715801930877894706
StaffTeam = 719848521813196951
# Cata Update Frequency
second = 0
minute = 15
hour = 0



# =================================================================================
#
#  THIS CODE IS IN NO WAY MY PROPERTY AND IS A EDITED VERSION OF THE ORIGINIAL TO ALLOW ASYNC SLEEP INSEAD OF SYNC SLEEP
#
# =================================================================================
'''
Rate limit public interface.

This module includes the decorator used to rate limit function invocations.
Additionally this module includes a naive retry strategy to be used in
conjunction with the rate limit decorator.
'''
from functools import wraps
from math import floor

import time
import sys
import threading

import time

def now():
    '''
    Use monotonic time if available, otherwise fall back to the system clock.

    :return: Time function.
    :rtype: function
    '''
    if hasattr(time, 'monotonic'):
        return time.monotonic
    return time.time


class RateLimitException(Exception):
    '''
    Rate limit exception class.
    '''
    def __init__(self, message, period_remaining):
        '''
        Custom exception raise when the number of function invocations exceeds
        that imposed by a rate limit. Additionally the exception is aware of
        the remaining time period after which the rate limit is reset.

        :param string message: Custom exception message.
        :param float period_remaining: The time remaining until the rate limit is reset.
        '''
        super(RateLimitException, self).__init__(message)
        self.period_remaining = period_remaining


class limits(object): # Formally Known As RateLimitDecorator(object):
    '''
    Rate limit decorator class.
    '''
    def __init__(self, calls=15, period=900, clock=now(), raise_on_limit=True):
        '''
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default the Twitter rate limiting window is respected (15 calls every
        15 minutes).

        :param int calls: Maximum function invocations allowed within a time period.
        :param float period: An upper bound time period (in seconds) before the rate limit resets.
        :param function clock: An optional function retuning the current time.
        :param bool raise_on_limit: A boolean allowing the caller to avoiding rasing an exception.
        '''
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.clock = clock
        self.raise_on_limit = raise_on_limit

        # Initialise the decorator state.
        self.last_reset = clock()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, func):
        '''
        Return a wrapped function that prevents further function invocations if
        previously called within a specified period of time.

        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        '''
        @wraps(func)
        def wrapper(*args, **kargs):
            '''
            Extend the behaviour of the decorated function, forwarding function
            invocations previously called no sooner than a specified period of
            time. The decorator will raise an exception if the function cannot
            be called so the caller may implement a retry strategy such as an
            exponential backoff.

            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyworded variable length argument list to the decorated function.
            :raises: RateLimitException
            '''
            with self.lock:
                period_remaining = self.__period_remaining()

                # If the time window has elapsed then reset.
                if period_remaining <= 0:
                    self.num_calls = 0
                    self.last_reset = self.clock()

                # Increase the number of attempts to call the function.
                self.num_calls += 1

                # If the number of attempts to call the function exceeds the
                # maximum then raise an exception.
                if self.num_calls > self.clamped_calls:
                    if self.raise_on_limit:
                        raise RateLimitException('too many calls', period_remaining)
                    return

            return func(*args, **kargs)
        return wrapper

    def __period_remaining(self):
        '''
        Return the period remaining for the current rate limit window.

        :return: The remaing period.
        :rtype: float
        '''
        elapsed = self.clock() - self.last_reset
        return self.period - elapsed

async def AsyncSleep( time ):
    await asyncio.sleep( time )

async def sleep_and_retry(func):
    '''
    Return a wrapped function that rescues rate limit exceptions, sleeping the
    current thread until rate limit resets.

    :param function func: The function to decorate.
    :return: Decorated function.
    :rtype: function
    '''
    @wraps(func)
    async def wrapper(*args, **kargs):
        '''
        Call the rate limited function. If the function raises a rate limit
        exception sleep for the remaing time period and retry the function.

        :param args: non-keyword variable length argument list to the decorated function.
        :param kargs: keyworded variable length argument list to the decorated function.
        '''
        while True:
            try:
                return func(*args, **kargs)
            except RateLimitException as exception:
                #time.sleep(exception.period_remaining)
                #asyncio.run( AsyncSleep( exception.period_remaining ) )
                await AsyncSleep( exception.period_remaining ) )
    return wrapper

# =================================================================================
#
#  THIS CODE IS IN NO WAY MY PROPERTY AND IS A EDITED VERSION OF THE ORIGINIAL TO ALLOW ASYNC SLEEP INSEAD OF SYNC SLEEP
#
# ==============================================================================




















# ===============================================================================================================
#  Actual Code Below
# ===============================================================================================================
client.remove_command("help")

def MongoCon(typ):
  client = pymongo.MongoClient("mongodb+srv://QueueBot:{}@queue.fz4sz.mongodb.net/discord?retryWrites=true&w=majority".format(os.environ["MONPY"]))
  if typ == "users":
    return client.discord.userlink
  elif typ == "config":
    return client.discord.config



@sleep_and_retry
@limits( calls = 100, period = 60 )
def HypixelConnection( endpoint, **kwargs ):
  ot = ""
  if kwargs:
    for k, v in kwargs.items( ):
      ot += f"&{ k }={ v }"
  r = requests.get("https://api.hypixel.net/"+endpoint+"?key="+os.environ["HYPY"]+ot)
  json = r.json()
  status = r.status_code
  return [json, status]



def find(exp):
  j, n = MongoCon("config").find_one({"_id":"Dungeons_Level_Exp"}), 0
  #j is json of all exp, n is level of catacombs
  
  for toBeSubtracted in j[ 'info' ]:
    exp -= toBeSubtracted
    if exp <= 0: 
      return n # + ( 1 - ( exp * -1 ) / toBeSubtracted )      More In Depth
    n += 1
  return 50


@client.event
async def on_ready():
  print("Logged in as " + client.user.name + "#" + client.user.discriminator)
  await Update_Users.start()


@client.command() 
async def help(ctx):
  guild = client.get_guild(SSB)
  arole = get(guild.roles, id=StaffTeam)
  brole = get(guild.roles, id=846825420993331203)
  Help = discord.Embed(title=f"{client.user.name}#{client.user.discriminator}'s Comand Help Page", description=f"**Bot Prefix**=`{prefix}`")
  Help.set_footer(text="Don't DM Knei#4714 with complaints")
  Help.add_field(name="link", value= f"aliases: `[\"l\"]`\nCommand: `{prefix}link <IGN>`\nIf you need link help replace IGN with help\nRoles Required: `Jr Carrier, Sr Carrier`")
  #Help.add_field(name="sync", value=f"aliases: `[\"s\"]`\nCommand: `{prefix}`sync`\nUseful for non carriers who want to update their rank name for some reason.[Note you will have to have run `{prefix}link [IGN]` before doing this]")
  Help.add_field(name="ScamCheck",value=f"aliases: `[\"sc\"]`\nCommand: `{prefix}ScamCheck <IGN>`\nAsk Delta Why This Was Needed again")
  if arole or brole in ctx.author.roles:
    Help.add_field(name="removeuser", value=f"aliases: `[ru, deleteuser, du]`\nCommand: `{prefix}removeuser <User>`\nRoles Required: `Carrier Manager, Staff Team`")
    Help.add_field(name="massremoveusers", value=f"aliases: `[mru, massdeleteuser, mdu]\nCommand: `{prefix}massremoveusers [users as mentions or IDs]`")
  try:
    await ctx.author.send(embed=Help)
    await ctx.send("Check your DM's")
  except:
    await ctx.send(embed=Help)


@tasks.loop( seconds=second, minutes=minute, hours=hour )
async def Update_Users( ):

  Total = UsersUp = UsersNo = UserUnknown = 0
  mon = MongoCon( 'users' )
  guild = client.get_guild(SSB)
  ST = get(guild.roles, id=StaffTeam).members
  JC = get(guild.roles, id=843249027411607552)
  SC = get(guild.roles, id=843248725190508564)
  MC = get(guild.roles, id=858362359570366484)
  UC = get(guild.roles, id=858362408706506833)
  AC = JC.members + SC.members + MC.members + UC.members 

  print( "Update has started!" )

  for profile in mon.find( ):
    discord = guild.get_member( int( profile[ "_id" ] ) )
    if discord:
      Total += 1
      if discord in AC and discord not in ST:
        #try:
          j, s = HypixelConnection( "skyblock/profile", profile = profile[ "profile" ])
          if s != 204 and s < 400:
            Level = find( j[ "profile" ][ "members" ][ profile[ "uuid" ] ][ "dungeons" ][ "dungeon_types" ][ "catacombs" ][ "experience" ] )
            if not discord.nick or discord.nick != f"[{ Level }] { profile[ 'ign' ]}":
              await discord.edit( nick = f"[{ Level }] { profile[ 'ign' ] }" )
              UsersUp += 1
              if discord not in SC + MC + UC and Level == 32:
                await discord.add_roles( roles = [ SC ], reason = "Meets requirements for Senior Carrier")
                await discord.remove_roles( roles = [ JC ], reason = "Met requirements for Senior Carrier")
            else: 
              UsersNo += 1
          else: 
            UserUnknown += 1
        #except:
        #  print( profile )
        #  UserUnknown += 1
      else: 
        UserUnknown += 1
    else: 
      UserUnknown += 1

  print( "Update has finished!" )
  print("Users Updated: {:2.1%}\nUsers Not Changed: {:2.1%}\nUsers Ignored/Not Found: {:2.1%}\nTotal Users: {}".format(UsersUp/Total, UsersNo/Total, UserUnknown/Total, Total))

#  print("Updating...")
#  for x in MongoCon("users").find():
#    Total +=1
#    try:  user = guild.get_member(int(x["_id"]))
#    except:  pass
#    else:  
#      try:
#        if user is not None:  
#          if role in user.roles: 
#            UserUnknown+=1
#          elif Sr in user.roles or Jr in user.roles:
#            j, s = await HypixelCon("skyblock/profile", profile = x["profile"])
#            if s == 200 and j["success"] == True: 
#              rank = await find(j["profile"]["members"][x["uuid"]]["dungeons"]["dungeon_types"]["catacombs"]["experience"])
#            else: raise Exception
#            if user.nick != None:   
#              onick = user.nick
#            else:   
#              onick = None
#            nnick = f"[{rank}] {x['ign']}"
#            if onick != nnick:
#              await user.edit(nick = nnick)
#              UsersUp+=1  
#            else:   UsersNo+=1 
#            if Sr not in user.roles and int(rank) >= 32:
#              await user.add_roles(roles=Sr,reason="Meet catacombs requirments")
#              await user.remove_roles(roles=Jr,reason="Has Senior Carrier")
#          else:   UsersNo+=1
#        else:   UserUnknown+=1
#      except:   UserUnknown+=1
#  print("Update Finished!")
#  if Total !=0: print("Users Updated: {:2.1%}\nUsers Not Changed: {:2.1%}\nUsers Ignored/Not Found: {:2.1%}\nTotal Users: {}".format(UsersUp/Total, UsersNo/Total, UserUnknown/Total, Total))
#  else: print("No users in database")


@Update_Users.error
async def on_error(ctx, error):
  Knei = client.get_guild(SSB).get_member(owner)
  await Knei.send(error)#.replace(os.environ["HYPY"], "KEY"))


@client.event
async def on_command_error(ctx, error):
  Knei = client.get_guild(SSB).get_member(owner)
  await Knei.send(error)#.replace(os.environ["HYPY"], "KEY"))








hel = """```scala
1. Type "/profile" in the in-game chat and press enter
2. Find the icon called "Social Media"
3. Find the icon called "Discord"
4. Go to the Discord app and click on your name on the bottom left to copy your Discord tag (eg: Knei#4714[capitalization matters])
5. Go back in game and paste that copied tag in the chat
6. If a book pops up, click "I understand"
```"""

@client.command( aliases = [ "l" ] )
@commands.has_any_role( 843249027411607552, 843248725190508564, 858362359570366484, 858362408706506833, 719848521813196951 )
async def link( ctx, User = None ):

  guild = client.get_guild( SSB )
  ST = get( guild.roles, id = StaffTeam ).members
  con = MongoCon("users")

  if not User:
    return await ctx.send( "Please provide a username!" )
  if User.lower() == 'help':
    return await ctx.send( hel )
  if con.find_one( { "_id" : ctx.author.id }.count( ) ) > 0:
    return await ctx.send( "You are already linked to " + str(con.find( { "_id" : ctx.author.id } )[ "ign" ] ) )
  if con.find_one( { "ign" : User } ).count( ) > 0:
    return await ctx.send( "This Username is already linked to another user!" )
  UUID = MojangAPI.get_uuid( User )
  if UUID:
    j1, s1 = HypixelConnection( "player", uuid = UUID )
    if s1 != 204 and s1 < 400:
      try:
        Discord = j1[ "player" ][ "socialMedia" ][ "links" ][ "DISCORD" ]
      except: 
        return await ctx.send( f"{ User } as no linked Discord Accounts\n" + hel )
      if Discord == ctx.author:
        j2, s2 = HypixelConnection( "skyblock/profiles", uuid = UUID )
        if s2 != 200 and s2 < 400:
          Profile, CataExp = "", 0
          for x in j2[ "profiles" ]:
            if x[ "members" ][ UUID ][ "dungeons"]["dungeon_types"]["catacombs"]["experience"] > CataExp:
              CataExp = x[ "members" ][ UUID ][ "dungeons"]["dungeon_types"]["catacombs"]["experience"]
              Profile = x
          CataLevel = find( CataExp )
          if ctx.author not in ST:
            await ctx.author.edit( nick = f"[{ CataLevel }] { User }")
          con.insert_one( { "ign":User, "_id":ctx.author.id, "uuid":UUID ,"profile":Profile } )
          await ctx.send( f"Successfully Linked to { User }!" )
        else:
          return await ctx.send( "There was an error connecting to Hypixels `skyblock/profiles` endpoint!" )
      else:
        return await ctx.send( "The given Discord Name doesnt match Yours!" )
    else:
      return await ctx.send( "There was an error connecting to Hypixels `player` endpoint!" )
  else:
    return await ctx.send( f"{ User } is not a valid Minecraft Account!" )
  
#  if User.lower() != "help":
#    if User != None:
#      UUID = MojangAPI.get_uuid(User)
#      User = MojangAPI.get_username(UUID)
#      for x in con.find():
#        if x["_id"] == ctx.author.id:
#          if Jr or Sr in ctx.author.roles:
#            await ctx.send("You are already linked!")
#            return
#        elif x["uuid"] == UUID: 
#          await ctx.send("This minecraft account is already linked!")
#          return
#      if UUID != None:
#        j, s = await HypixelCon("player",uuid=UUID)
#        if s == 200:
#          try:  
#            discord = j["player"]["socialMedia"]["links"]["DISCORD"]
#          except KeyError: 
#            await ctx.send(User + " has no linked discord account.\n"+hel)
#          if str(discord)==str(ctx.author):
#            l = []
#            j, s = await HypixelCon("skyblock/profiles", uuid = UUID)
#            if s == 200:
#              for x in j["profiles"]: 
#                try:  
#                  l.append(x["members"][f"{UUID}"]["dungeons"]["dungeon_types"]["catacombs"]["experience"])
#                except:
#                  pass
#              level = await find(max(l))
#              for x in j["profiles"]:
#                try:
#                  if max(l) == x["members"][f"{UUID}"]["dungeons"]["dungeon_types"]["catacombs"]["experience"]:
#                    profile = x["profile_id"]
#                except: pass
#              try:
#                if role not in ctx.author.roles:
#                  await ctx.author.edit(nick=f"[{level}] {User}")
#                  con.insert_one({"ign":User, "_id":ctx.author.id, "uuid":UUID ,"profile":profile})
#                  await ctx.send("Successfully Linked")   
#                else: 
#                  con.insert_one({"ign":User, "_id":ctx.author.id, "uuid":UUID ,"profile":profile})
#                  await ctx.send("Successfully Linked")   
#
#    #Was lazy so I shoved all the fails down here
#              except: await ctx.send("There was an error. Please Try again.")
#            else: await ctx.send("Failed to connect to the skyblock profile endpoint.\nPlease try again.")
#          else: await ctx.send("The given discord does not match yours")  
#        else: await ctx.send("Failed to connect to Hypixel API please try again\nIf this happens multiple times the API might be down")
#      else: await ctx.send("Invalid username")
#    else: await ctx.send("Please provide a username")
#  else: await ctx.send(hel)

@client.command(aliases = ["ru", "deleteuser", "du"])
@commands.has_any_role(719848521813196951, 846825420993331203)
async def removeuser(ctx, user: discord.Member):
  try:
    MongoCon("users").delete_one({"_id":user.id})
    await ctx.send("User Removed!")
  except:
    await ctx.send("User Not Found")


@client.event 
async def on_member_remove(member):
  try:
    MongoCon("users").delete_one({"_id":member.id})
  except:
    await asyncio.sleep(60)
    MongoCon("users").delete_one({"_id":member.id})


@client.command(aliases = ["mru", "massdeleteuser", "mdu"])
@commands.has_any_role(719848521813196951, 846825420993331203)
async def massremoveusers(ctx, *user: discord.Member):
  Removed = NotFound = 0
  l = []
  con = MongoCon("users")
  msg = await ctx.send("Deleting Users...")
  for x in user:
    for y in con.find():
      if y["_id"] == x.id:
        con.delete_one(x)
        Removed +=1 
    l.append(x)
    NotFound +=1
  if NotFound != 0:
    message = f"\nRemoved {Removed} users with {NotFound} users skipped due to not being found||(And maybe an error)||.\nUsers Skipped:\n"
    for x in l:
      message += f"{x.mention}[{x.id}], "
  else:
    message = f"\nAll {Removed} users removed!"
  await msg.edit(content=f"Purge Completed!{message[:-2]}")


@client.command(aliases = ["sc"])
async def ScamCheck(ctx, IGN=None):
  await ctx.send("Deprecated For Now.")
  #if IGN != None:
  #  uuid = MojangAPI.get_uuid(IGN)
  #  if uuid != None:
  #    reply = requests.get("https://api.skybrokers.xyz/scammer?uuid="+uuid).json()
  #    if "scammer" in reply: await ctx.send(IGN + " is not on the scammer list!")
  #    else: await ctx.send(IGN + " is on the scammer list!")
  #  else: await ctx.send("Please Provide a Valid Username!")
  #else: await ctx.send("Please Provide a Username!")
    
  
#@client.command(aliases = ["s"])
#async def sync(ctx):
#  name=""
#  con = MongoCon("users")
#  for x in con.find():
#    if x["_id"] == ctx.author.id:
#      j, s = await HypixelCon("skyblock/profile", profile=x["profile"])
#      if s == 200:
#        if ctx.author.nick != None:
#          name = ctx.author.nick
#        else:
#          name = ctx.author.name
#        level = await find(j["profile"]["members"][x["uuid"]]["dungeons"]["dungeon_types"]["catacombs"]["experience"])
#        await ctx.author.edit(nick=f"[{level}] {name}")
#        await ctx.send("Cata Level Updated!")
#        return
#      else: 
#        await ctx.send("There was an error connecting to hypixel API")
#        return
#  await ctx.send("You aren't linked!")


@client.command()
@commands.has_any_role(719848521813196951, 846825420993331203)
async def runThrough(ctx):
  con = MongoCon("users")
  guild = client.get_guild(SSB)
  mod = get(guild.roles, id=StaffTeam).members
  Jr = get(guild.roles, id=843249027411607552).members
  Sr = get(guild.roles, id=843248725190508564).members
  li = [Jr, Sr]
  l, strs = [], ""
  msg = await ctx.send("Searching...")
  for z in li:
    for y in z:
      r=con.find_one({"_id":y.id})
      if type(r) != dict:
        if y not in mod:
            l.append( y.id )
  msg1 = await ctx.send( "Missing Users:" )
  for x in l:
    strs += "<@{}>[{}]\n".format( x, x )
  await msg1.edit( content=msg1.content+"\n"+ strs +"\nTotal Missing: "+str( len( l ) ) )
  await msg.edit( content="Search completed" )



client.run( os.environ[ "Carrier" ] )

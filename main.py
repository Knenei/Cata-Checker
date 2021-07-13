import os
import asyncio
import discord
import pymongo
import requests
from ratelimit import limits, RateLimitException
from mojang import MojangAPI
from discord.utils import get
from discord.ext import commands, tasks
from datetime import datetime, timedelta


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
minute = 10
hour = 0

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

@limits( calls = 120, period = 60 )
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
    print( profile[ "ign" ], discord )  
    if discord:
      Total += 1
      if discord in AC and discord not in ST:
        try:
          j, s = HypixelConnection( "skyblock/profile", profile = profile[ "profile" ])
        except RateLimitException as exception:
          await asyncio.sleep( exception.period_remaining )
          j, s = HypixelConnection( "skyblock/profile", profile = profile[ "profile" ])
        if s != 204 and s < 400:
          Level = find( j[ "profile" ][ "members" ][ profile[ "uuid" ] ][ "dungeons" ][ "dungeon_types" ][ "catacombs" ][ "experience" ] )
          if not discord.nick or discord.nick != f"[{ Level }] { profile[ 'ign' ]}":
            await discord.edit( nick = f"[{ Level }] { profile[ 'ign' ] }" )
            UsersUp += 1
            if discord not in SC.members + MC.members + UC.members and Level >= 32:
              await discord.add_roles( roles = [ SC ], reason = "Meets requirements for Senior Carrier")
              await discord.remove_roles( roles = [ JC ], reason = "Met requirements for Senior Carrier")
          else: 
            UsersNo += 1
        else: 
          print( discord )
          UserUnknown += 1
      else: 
        print( discord )
        UserUnknown += 1
    else: 
      print( discord ) 
      UserUnknown += 1

  print( "Update has finished!" )
  print("Users Updated: {:2.1%}\nUsers Not Changed: {:2.1%}\nUsers Ignored/Not Found: {:2.1%}\nTotal Users: {}".format(UsersUp/Total, UsersNo/Total, UserUnknown/Total, Total))


@Update_Users.error
async def on_error(ctx, error):
  Knei = client.get_guild(SSB).get_member(owner)
  await Knei.send(error)#.replace(os.environ["HYPY"], "KEY"))


#@client.event
#async def on_command_error(ctx, error):
#  Knei = client.get_guild(SSB).get_member(owner)
#  await Knei.send(error)#.replace(os.environ["HYPY"], "KEY"))




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
  if con.count_documents( { '_id': ctx.author.id }, limit = 1 ) != 0:
    return await ctx.send( "You are already linked to " + str(con.find( { "_id" : ctx.author.id } )[ "ign" ] ) )
  if con.count_documents( { 'ign': User }, limit = 1 ) != 0:
    return await ctx.send( "This Username is already linked to another user!" )
  UUID = MojangAPI.get_uuid( User )
  if UUID:
    j1, s1 = HypixelConnection( "player", uuid = UUID )
    if s1 != 204 and s1 < 400:
      try:
        Discord = j1[ "player" ][ "socialMedia" ][ "links" ][ "DISCORD" ]
      except: 
        return await ctx.send( f"{ User } has no linked Discord Accounts\n" + hel )
      if str( Discord ) == str( ctx.author ):
        j2, s2 = HypixelConnection( "skyblock/profiles", uuid = UUID ) 
        if s2 != 204 and s2 < 400:
          Profile, CataExp = "", 0
          for x in j2[ "profiles" ]:
            try:
              if x[ "members" ][ UUID ][ "dungeons"]["dungeon_types"]["catacombs"]["experience"] > CataExp:
                CataExp = x[ "members" ][ UUID ][ "dungeons"]["dungeon_types"]["catacombs"]["experience"]
                Profile = x[ "profile_id" ]
            except KeyError:
              pass
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
  

@client.command( aliases = [ "ru", "deleteuser", "du" ] )
@commands.has_any_role( 719848521813196951, 846825420993331203 )
async def removeuser( ctx, user: discord.Member ):
  try:
    MongoCon( "users" ).delete_one( { "_id":user.id } )
    await ctx.send( "User Removed!" )
  except:
    await ctx.send( "User Not Found" )


@client.event 
async def on_member_remove( member ):
  try:
    MongoCon( "users" ).delete_one( { "_id":member.id } )
  except:
    await asyncio.sleep( 60 )
    MongoCon( "users" ).delete_one( { "_id":member.id } )


@client.command( aliases = [ "mru", "massdeleteuser", "mdu" ] )
@commands.has_any_role( 719848521813196951, 846825420993331203 )
async def massremoveusers( ctx, *user: discord.Member ):
  Removed = NotFound = 0
  l = [ ]
  con = MongoCon( "users" )
  msg = await ctx.send( "Deleting Users..." )
  for x in user:
    for y in con.find( ):
      if y[ "_id" ] == x.id:
        con.delete_one( x )
        Removed +=1 
    l.append( x )
    NotFound +=1
  if NotFound != 0:
    message = f"\nRemoved { Removed } users with { NotFound } users skipped due to not being found||(And maybe an error)||.\nUsers Skipped:\n"
    for x in l:
      message += f"{ x.mention }[{ x.id }], "
  else:
    message = f"\nAll { Removed } users removed!"
  await msg.edit( content = f"Purge Completed!{ message[ :-2 ] }" )


@client.command( aliases = [ "sc" ] )
async def ScamCheck( ctx, IGN=None ):
  await ctx.send( "Deprecated For Now." )
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


@client.command( )
@commands.has_any_role( 719848521813196951, 846825420993331203 )
async def runThrough( ctx ): #, Warn = None ):
  con = MongoCon( "users" )
  guild = client.get_guild( SSB )
  ST = get( guild.roles, id = StaffTeam ).members
  CM = get( guild.roles, id = 846825420993331203 ).members
  JC = get( guild.roles, id = 843249027411607552 ).members
  SC = get( guild.roles, id = 843248725190508564 ).members
  MC = get( guild.roles, id = 858362359570366484 ).members
  UC = get( guild.roles, id = 858362408706506833 ).members
  AC = [ x for x in [ UC + MC + SC + JC ] if x not in [ ST + CM ] ]
  Members, strs, fail = [  ], "", ""
  search = await ctx.send( "Searching..." )
  for member in AC:
    if con.count_documents( { '_id': member.id }, limit = 1 ) == 0:
      Members.append( member.id )
  await search.edit( "Search Completed Returning Results..." )
  if Members[ 0 ]:
    Initial = await ctx.send( "Missing Members:" )
    for member in Members:
      strs += "<@{ 0 }>[{ 0 }]\n".format( member )
    await Initial.edit( content = Initial.content + strs )  
    #if Warn:
    #  await ctx.send( "Preparing to DM users" )
    #  await asyncio.sleep( 5 )
    #  Warn = await ctx.send( "Users DM Status:" )
    #  for member in Members:
    #    try:
    #      await guild.get_member( member ).send( "```scala\nHello {0} it seems like you arent in the DataBase for linked users!\nPlease run \"%link <YOUR_IGN>\" as soon as you can in ▹carrier-bot-commands.\n1 Week after you recieve this message you will be STRIKED. \nSKY | Brokers Dungeons Management\n```\n||This was an automated message any reply wont do much because I don't thing there will be a reason to reply||".format( await guild.get( member ).name ) )
    #    except:
    #      fail += "<@{ 0 }>".format( member )
    #  await Warn.edit( content = Warn.content + "\n" + fail )
  else:
    await ctx.send( "All Carriers Are In The Database" )



client.run( os.environ[ "Carrier" ] )

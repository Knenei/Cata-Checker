import os
# config (Update as you see fit)
prefix = '$'
MasterGuild = os.environ["MGUILD"]
# Cata Update Frequency
second = 0
minute = 1
hour = 0

#Code
import json
import aiohttp
import discord
import pymongo
from discord.ext import commands, tasks
from mojang import MojangAPI

client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all(), case_insensitive = True)

def MongoCon():
  client = pymongo.MongoClient(f"mongodb+srv://QueueBot:{os.environ['MONPY']}@queue.fz4sz.mongodb.net/discord?retryWrites=true&w=majority")
  return client.discord.userlink


async def HypixelCon(endpoint, **kwargs):
  other = ""
  if kwargs: 
    for key, val in kwargs.items():
      other += f"&{key}={val}"
  async with aiohttp.ClientSession() as s:
    async with s.request("GET", "https://api.hypixel.net/"+endpoint+"?key="+os.environ["HYPY"]+other) as r:
      _json = await r.json()
      _status = r.status
      return _json, _status


async def find(exp:int):
  n = -1
  with open('./Dungeon.json') as j:
    j = json.load(j)
  for x in j:
    if x['total'] > exp:
      return n
    n+=1
  return 50

@client.event
async def on_ready():
  print("Logged in as " + client.user.name + '#' + client.user.discriminator)
  await Update_Users.start()


@tasks.loop(seconds=second, minutes=minute, hours=hour)
async def Update_Users():
  guild = client.get_guild(MasterGuild)
  for x in MongoCon().find():
    try:
      user = guild.get_member(x["_id"])
      j, s = await HypixelCon("skyblock/profile", profile = x["profile"])
    except:   pass
    
    if s != 200 or j["success"] != True: pass 
    else:
      rank = await find(j['profile']['members'][f"{x['uuid']}"]['dungeons']['dungeon_types']["catacombs"]["experience"])
      
      if user.nick != None: 
        nick = user.nick[4:]
        if " " in nick[:1]:
          nick.replace(" ", '', 1)
      else: nick = user.name
      await user.edit(nick = f'[{rank}] {nick}')

@client.command(aliases = ['l', 'link', 's'])
async def sync(ctx, User=None):
  con = MongoCon()
  if User != None:
    UUID = MojangAPI.get_uuid(User)
    
    for x in con.find():
      
      if x['_id'] == ctx.author.id: 
        await ctx.send('You are already linked!')
        return
      elif x['uuid'] == UUID: 
        await ctx.send('This minecraft account is already linked!')
        return

    if UUID != None:
      
      j, s = await HypixelCon('player',uuid=UUID)
      
      if s == 200:
        
        try:    
        
          discord = j['player']['socialMedia']['links']['DISCORD']
        
        except KeyError:    
        
          await ctx.send(User + " has no linked discord account")
        
        if str(discord)==str(ctx.author):
         
          l = []
          j, s = await HypixelCon("skyblock/profiles", uuid = UUID)
          
          if s == 200:
            
            for x in j['profiles']: 
              
              try:    
                l.append(x['members'][f'{UUID}']['dungeons']['dungeon_types']["catacombs"]["experience"])
                profile = x['profile_id']
              except:   pass

            try: 
              nick = ctx.author.nick[:26]
            except: 
              nick = ctx.author.name[:26]

            try:
              await ctx.author.edit(nick=f'[{await find(max(l))}] {nick}')
              con.insert_one({"_id":ctx.author.id, "uuid":UUID, "profile":profile})
              await ctx.send('Successfully Linked')
            
#Was lazy so I shoved all the fails down here
            except: await ctx.send('There was an error. Please Try again')
          else: await ctx.send('Failed to connect to the skyblock profile endpoint.\nPlease try again.')
        else: await ctx.send('The given discord does not match yours')  
      else: await ctx.send('Failed to connect to Hypixel API please try again\nIf this happens multiple times the API might be down')
    else: await ctx.send('Invalid username')
  else: await ctx.send('Please provide a username')


if __name__ == '__main__': client.run(os.environ["Carrier"])
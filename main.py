import os
import json
import asyncio
import aiohttp
import discord
import pymongo
from mojang import MojangAPI
from discord.utils import get
from discord.ext import commands, tasks


# config (Update as you see fit)
prefix = '$'
client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all(), case_insensitive = True) 
#please dont mess with ^^^^ thanks :)
masterguild = int(os.environ["MGUILD"])

# Cata Update Frequency
second = 0
minute = 1
hour = 0

#Code


def MongoCon():
    client = pymongo.MongoClient("mongodb+srv://QueueBot:{}@queue.fz4sz.mongodb.net/discord?retryWrites=true&w=majority".format(os.environ['MONPY']))
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
    Total = UsersUp = UsersNo = UserUnknown = 0
    guild = client.get_guild(masterguild)
    role = discord.utils.get(guild.roles, id=719848521813196951)
    print("Updating...", end='\r')
    for x in MongoCon().find():
        Total +=1
        try:
            user = guild.get_member(x["_id"])
        except: pass
        else:
            try:
                if role not in user.roles:
                    if user != None:
                        j, s = await HypixelCon("skyblock/profile", profile = x["profile"])
                        if s != 200 or j["success"] != True: pass 
                        else:
                            rank = await find(j['profile']['members'][f"{x['uuid']}"]['dungeons']['dungeon_types']["catacombs"]["experience"])
                        if user.nick != None:   
                            onick = user.nick
                        else:   
                            onick = None
                        nnick = f"[{rank}] {x['ign']}"
                        if onick == nnick:  
                            UsersNo+=1
                        else: 
                            UsersUp+=1
                            await user.edit(nick = nnick)
                    else: UserUnknown+=1
                else: UsersNo+=1
            except: UserUnknown+=1
    print("Update Finished!")
    print("\rUsers Updated: {:2.1%}\nUsers Not Changed: {:2.1%}\nNot Found: {:2.1%}\nTotal Users: {}".format(UsersUp/Total, UsersNo/Total, UserUnknown/Total, Total))

      

@client.command(aliases = ['l', 'link', 's'])
@commands.has_any_role(843249027411607552, 843248725190508564, 719848521813196951)
async def sync(ctx, User=None):
    con = MongoCon()
    if User != None:
        UUID = MojangAPI.get_uuid(User)
        User = MojangAPI.get_username(UUID)
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
                        await ctx.send(User + " has no linked discord account.\nLink an account by going ingame\n ```scala\nPlayer Head > Social > Discord\n```")
                    if str(discord)==str(ctx.author):
                        l = []
                        j, s = await HypixelCon("skyblock/profiles", uuid = UUID)
                        if s == 200:
                            for x in j['profiles']: 
                                try:    
                                    l.append(x['members'][f'{UUID}']['dungeons']['dungeon_types']["catacombs"]["experience"])
                                except:   pass
                                level = await find(max(l))
                                for x in j['profiles']:
                                    try:
                                        if max(l) == x['members'][f'{UUID}']['dungeons']['dungeon_types']["catacombs"]["experience"]:
                                            profile = x["profile_id"]
                                    except: pass
                                    try:
                                        guild = client.get_guild(masterguild)
                                        role = get(guild.roles, id=847470285330710538)#719848521813196951)
                                        if role not in ctx.author.roles:
                                            await ctx.author.edit(nick=f'[{level}] {User}')
                                        else:
                                            con.insert_one({"_id":ctx.author.id, "uuid":UUID,"ign":User ,"profile":profile})
                                            await ctx.send('Successfully Linked')   

#Was lazy so I shoved all the fails down here
                                    except: await ctx.send('There was an error. Please Try again.')
                        else: await ctx.send('Failed to connect to the skyblock profile endpoint.\nPlease try again.')
                    else: await ctx.send('The given discord does not match yours')  
                else: await ctx.send('Failed to connect to Hypixel API please try again\nIf this happens multiple times the API might be down')
            else: await ctx.send('Invalid username')
    else: await ctx.send('Please provide a username')


@client.command(aliases = ["ru", "deleteuser", "du"])
@commands.has_any_role(719848521813196951, 719848521813196951)
async def removeuser(ctx, user: discord.Member):
    try:
        MongoCon().delete_one({"_id":user.id})
        await ctx.send("User Removed!")
    except:
        await ctx.send("User Not Found")


@client.event
async def on_member_remove(member):
    try:
        MongoCon().delete_one({"_id":member.id})
    except:
        await asyncio.sleep(60)
        MongoCon().delete_one({"_id":member.id})

client.run(os.environ["Carrier"])
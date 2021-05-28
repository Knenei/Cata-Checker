import os
import asyncio
import aiohttp
import discord
import pymongo
from mojang import MojangAPI
from discord.utils import get
from discord.ext import commands, tasks


# config (Update as you see fit)
prefix = '%'
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive = True)
#please dont mess with ^^^^ thanks :)
masterguild = int(os.environ["MGUILD"])
AdminRole = 719848521813196951
# Cata Update Frequency
second = 0
minute = 1
hour = 0

#Code
client.remove_command('help')

def MongoCon(typ):
    client = pymongo.MongoClient("mongodb+srv://QueueBot:{}@queue.fz4sz.mongodb.net/discord?retryWrites=true&w=majority".format(os.environ['MONPY']))
    if typ == 'users':
        return client.discord.userlink
    elif typ == 'config':
        return client.discord.config


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
    j = MongoCon('config').find({"_id":"Dungeons"})
    for x in j['info']:
        if x['total'] > exp:
            return n
        n+=1
    return 50


@client.event
async def on_ready():
    print("Logged in as " + client.user.name + '#' + client.user.discriminator)
    await Update_Users.start()


@client.command() 
async def help(ctx):
    Help = discord.Embed(title=f"{client.user.name}#{client.user.discriminator}'s Comand Help Page", description=f"**Bot Prefix**=`{prefix}`")
    Help.set_footer(text="Don't DM Knei#4714 with complaints")
    Help.add_field(name="link",value= f"aliases: `['sync', 's', 'l']`\nCommand: `{prefix}link <IGN>`\nRoles Required: `Jr Carrier, Sr Carrier`")
    try:
        await ctx.author.send(embed=Help)
        await ctx.send("Check your DM's")
    except:
        await ctx.send()


@tasks.loop(seconds=second, minutes=minute, hours=hour)
async def Update_Users():
    Total = UsersUp = UsersNo = UserUnknown = 0
    guild = client.get_guild(masterguild)
    role = discord.utils.get(guild.roles, id=AdminRole)
    print("Updating...")
    for x in MongoCon('users').find():
        Total +=1
        print(1)
        try:    
            user = guild.get_member(int(x["_id"]))
            print(2)
        except:     
            print(3)
            pass
        else:  
            print(4)
            print(role)
            print(user.roles)
            try:
                print(5)
                if role in user.roles: 
                    UserUnknown+=1
                    print(6)
                else:
                    print(7)
                    if user == None:  
                        UsersNo+=1
                        print(8)
                    else: 
                        print(9)
                        j, s = await HypixelCon("skyblock/profile", profile = x["profile"])
                        print(j, s)
                        if s != 200 or j["success"] != True: pass 
                        else:
                            print(10)
                            rank = await find(j['profile']['members'][f"{x['uuid']}"]['dungeons']['dungeon_types']["catacombs"]["experience"])
                        if user.nick != None:   
                            onick = user.nick
                            print(11)
                        else:   
                            onick = None
                            print(12)
                        nnick = f"[{rank}] {x['ign']}"
                        if onick == nnick:  
                            UsersNo+=1
                            print(13)
                        else: 
                            await user.edit(nick = nnick)
                            UsersUp+=1
                            print(14)
            except: 
                UserUnknown+=1
                print(15)
    print("Update Finished!")
    if Total !=0:
        print("\rUsers Updated: {:2.1%}\nUsers Not Changed: {:2.1%}\nNot Found: {:2.1%}\nTotal Users: {}".format(UsersUp/Total, UsersNo/Total, UserUnknown/Total, Total))
    else: print("No users in database")
      

@client.command(aliases = ['l', 'link', 's'])
@commands.has_any_role(843249027411607552, 843248725190508564, 719848521813196951, 847470285330710538)
async def sync(ctx, User=None):
    con = MongoCon('users')
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
                            role = get(guild.roles, id=AdminRole)
                            if role not in ctx.author.roles:
                                await ctx.author.edit(nick=f'[{level}] {User}')
                            else:
                                con.insert_one({"ign":User, "_id":ctx.author.id, "uuid":UUID ,"profile":profile})
                                await ctx.send('Successfully Linked')   

#Was lazy so I shoved all the fails down here
                        except: await ctx.send('There was an error. Please Try again.')
                    else: await ctx.send('Failed to connect to the skyblock profile endpoint.\nPlease try again.')
                else: await ctx.send('The given discord does not match yours')  
            else: await ctx.send('Failed to connect to Hypixel API please try again\nIf this happens multiple times the API might be down')
        else: await ctx.send('Invalid username')
    else: await ctx.send('Please provide a username')


@sync.error
async def on_sync_error(ctx, error):
    if isinstance(error, commands.errors.MissingAnyRole):
        await ctx.send("You don't have a carrier role!")
    else:
        pass


@client.command(aliases = ["ru", "deleteuser", "du"])
@commands.has_any_role(719848521813196951, 719848521813196951)
async def removeuser(ctx, user: discord.Member):
    try:
        MongoCon('users').delete_one({"_id":user.id})
        await ctx.send("User Removed!")
    except:
        await ctx.send("User Not Found")


@client.event 
async def on_member_remove(member):
    try:
        MongoCon('users').delete_one({"_id":member.id})
    except:
        await asyncio.sleep(60)
        MongoCon('users').delete_one({"_id":member.id})

client.run(os.environ["Carrier"])

import os
import asyncio
import aiohttp
import discord
import pymongo
import requests
from mojang import MojangAPI
from discord.utils import get
from discord.ext import commands, tasks


# config (Update as you see fit)
prefix = "%"
#please dont mess with ▽▽▽▽ thanks :)
intents = discord.Intents.default()
intents.members = True 
client = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive = True)
#please dont mess with △△△△ thanks :)
masterguild = int(os.environ["MGUILD"])
AdminRole = 719848521813196951
# Cata Update Frequency
second = 30
minute = 2
hour = 0

#Code
client.remove_command("help")

def MongoCon(typ):
    client = pymongo.MongoClient("mongodb+srv://QueueBot:{}@queue.fz4sz.mongodb.net/discord?retryWrites=true&w=majority".format(os.environ["MONPY"]))
    if typ == "users":
        return client.discord.userlink
    elif typ == "config":
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
    j, n = MongoCon("config").find_one({"_id":"Dungeons"}), 0
    for x in j["info"]:
        if x["total"] > exp:
            return n
        n+=1
    return 50


@client.event
async def on_ready():
    print("Logged in as " + client.user.name + "#" + client.user.discriminator)
    await Update_Users.start()


@client.command() 
async def help(ctx):
    guild = client.get_guild(masterguild)
    arole = get(guild.roles, id=AdminRole)
    brole = get(guild.roles, id=846825420993331203)
    Help = discord.Embed(title=f"{client.user.name}#{client.user.discriminator}'s Comand Help Page", description=f"**Bot Prefix**=`{prefix}`")
    Help.set_footer(text="Don't DM Knei#4714 with complaints")
    Help.add_field(name="link",value= f"aliases: `[\"l\"]`\nCommand: `{prefix}link <IGN>`\nIf you need link help replace IGN with help\nRoles Required: `Jr Carrier, Sr Carrier`")
    Help.add_field(name="sync", value=f"aliases: `[\"s\"]`\nCommand: `{prefix}`sync`\nUseful for non carriers who want to update their rank name for some reason.[Note you will have to have run `{prefix}link [IGN]` before doing this]")
    Help.add_field(name="ScamCheck",value=f"aliases: `[\"sc\"]`\nCommand: `{prefix}ScamCheck <IGN>`\nAsk Delta Why This Was Needed again")
    if arole or brole in ctx.author.roles:
        Help.add_field(name="removeuser", value=f"aliases: `[ru, deleteuser, du]`\nCommand: `{prefix}removeuser <User>`\nRoles Required: `Carrier Manager, Staff Team`")
        Help.add_field(name="massremoveusers", value=f"aliases: `[mru, massdeleteuser, mdu]\nCommand: `{prefix}massremoveusers [users as mentions or IDs]`")
    try:
        await ctx.author.send(embed=Help)
        await ctx.send("Check your DM's")
    except:
        await ctx.send(embed=Help)


@tasks.loop(seconds=second, minutes=minute, hours=hour)
async def Update_Users():
    Total = UsersUp = UsersNo = UserUnknown = 0
    guild = client.get_guild(masterguild)
    role = get(guild.roles, id=AdminRole)
    Jr = get(guild.roles, id=843249027411607552)
    Sr = get(guild.roles, id=843248725190508564)
    print("Updating...")
    for x in MongoCon("users").find():
        Total +=1
        try:    user = guild.get_member(int(x["_id"]))
        except:    pass
        else:  
            try:
                if user is not None:  
                    if role in user.roles: 
                        UserUnknown+=1
                    elif Sr in user.roles or Jr in user.roles:
                        j, s = await HypixelCon("skyblock/profile", profile = x["profile"])
                        if s == 200 and j["success"] == True: 
                            rank = await find(j["profile"]["members"][x["uuid"]]["dungeons"]["dungeon_types"]["catacombs"]["experience"])
                        else: raise Exception
                        if user.nick != None:   
                            onick = user.nick
                        else:   
                            onick = None
                        nnick = f"[{rank}] {x['ign']}"
                        if onick != nnick:
                            await user.edit(nick = nnick)
                            UsersUp+=1  
                        else:   UsersNo+=1 
                        if Sr not in user.roles and int(rank) >= 32:
                            await user.add_roles(roles=Sr,reason="Meet catacombs requirments")
                            await user.remove_roles(roles=Jr,reason="Has Senior Carrier")
                    else:   UsersNo+=1
                else:   UserUnknown+=1
            except:     UserUnknown+=1
    print("Update Finished!")
    if Total !=0: print("Users Updated: {:2.1%}\nUsers Not Changed: {:2.1%}\nUsers Ignored/Not Found: {:2.1%}\nTotal Users: {}".format(UsersUp/Total, UsersNo/Total, UserUnknown/Total, Total))
    else: print("No users in database")
      
hel = """```scala
1. Type "/profile" in the in-game chat and press enter
2. Find the icon called "Social Media"
3. Find the icon called "Discord"
4. Go to the Discord app and click on your name on the bottom left to copy your Discord tag (eg: Knei#4714[capitalization matters])
5. Go back in game and paste that copied tag in the chat
6. If a book pops up, click "I understand"
```"""

@client.command(aliases = ["l"])
#@commands.has_any_role(843249027411607552, 843248725190508564, 719848521813196951)
async def link(ctx, User=None):
    guild = client.get_guild(masterguild)
    role = get(guild.roles, id=AdminRole)
    Jr = get(guild.roles, id=843249027411607552)
    Sr = get(guild.roles, id=843248725190508564)
    con = MongoCon("users")
    if User.lower() != "help":
        if User != None:
            UUID = MojangAPI.get_uuid(User)
            User = MojangAPI.get_username(UUID)
            for x in con.find():
                if x["_id"] == ctx.author.id:
                    if Jr or Sr in ctx.author.roles:
                        await ctx.send("You are already linked!")
                        return
                elif x["uuid"] == UUID: 
                    await ctx.send("This minecraft account is already linked!")
                    return
            if UUID != None:
                j, s = await HypixelCon("player",uuid=UUID)
                if s == 200:
                    try:    
                        discord = j["player"]["socialMedia"]["links"]["DISCORD"]
                    except KeyError: 
                        await ctx.send(User + " has no linked discord account.\n"+hel)
                    if str(discord)==str(ctx.author):
                        l = []
                        j, s = await HypixelCon("skyblock/profiles", uuid = UUID)
                        if s == 200:
                            for x in j["profiles"]: 
                                try:    
                                    l.append(x["members"][f"{UUID}"]["dungeons"]["dungeon_types"]["catacombs"]["experience"])
                                except:
                                    pass
                            level = await find(max(l))
                            for x in j["profiles"]:
                                try:
                                    if max(l) == x["members"][f"{UUID}"]["dungeons"]["dungeon_types"]["catacombs"]["experience"]:
                                        profile = x["profile_id"]
                                except: pass
                            try:
                                if role not in ctx.author.roles:
                                    await ctx.author.edit(nick=f"[{level}] {User}")
                                    con.insert_one({"ign":User, "_id":ctx.author.id, "uuid":UUID ,"profile":profile})
                                    await ctx.send("Successfully Linked")   
                                else: 
                                    con.insert_one({"ign":User, "_id":ctx.author.id, "uuid":UUID ,"profile":profile})
                                    await ctx.send("Successfully Linked")   

        #Was lazy so I shoved all the fails down here
                            except: await ctx.send("There was an error. Please Try again.")
                        else: await ctx.send("Failed to connect to the skyblock profile endpoint.\nPlease try again.")
                    else: await ctx.send("The given discord does not match yours")  
                else: await ctx.send("Failed to connect to Hypixel API please try again\nIf this happens multiple times the API might be down")
            else: await ctx.send("Invalid username")
        else: await ctx.send("Please provide a username")
    else: await ctx.send(hel)

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
  await ctx.send("Currently broken cause rip.")
  #if IGN != None:
  #    uuid = MojangAPI.get_uuid(IGN)
  #    if uuid != None:
  #        reply = requests.get("https://api.skybrokers.xyz/scammer?uuid="+uuid).json()
  #        if "scammer" in reply: await ctx.send(IGN + " is not on the scammer list!")
  #        else: await ctx.send(IGN + " is on the scammer list!")
  #    else: await ctx.send("Please Provide a Valid Username!")
  #else: await ctx.send("Please Provide a Username!")
        
  
@client.command(aliases = ["s"])
async def sync(ctx):
    name=""
    con = MongoCon("users")
    for x in con.find():
        if x["_id"] == ctx.author.id:
            j, s = await HypixelCon("skyblock/profile", profile=x["profile"])
            if s == 200:
                if ctx.author.nick != None:
                    name = ctx.author.nick
                else:
                    name = ctx.author.name
                level = await find(j["profile"]["members"][x["uuid"]]["dungeons"]["dungeon_types"]["catacombs"]["experience"])
                await ctx.author.edit(nick=f"[{level}] {name}")

client.run(os.environ["Carrier"])

import keepalive
import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
import os
from replit import db
from commands.force_commands import ForceCommands
from commands.form_commands import FormCommands
from commands.user_commands import UserCommands
from commands.view_commands import ViewCommands
from submissions import SubmissionsCog
from shared import guildIds, adminRoles, validation

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

keepalive.keep_alive()
bot = discord.Bot(intents=intents)
token = os.environ['TOKEN']
guildids = guildIds


@bot.listen()
async def on_thread_udate(before, after):
    print("thread updated")
    if before.parent.type == discord.ChannelType.forum:
        newTags = after.appliedd_tags - before.applied_tags
        tagNames = [tag.name for tag in newTags]
        if "test" in tagNames:
            await after.send("it works")


def setup(bot):
    bot.add_cog(Dev(bot), override=True)
    bot.add_cog(FormCommands(bot), override=True)
    bot.add_cog(ForceCommands(bot), override=True)
    bot.add_cog(UserCommands(bot), override=True)
    bot.add_cog(ViewCommands(bot), override=True)
    bot.add_cog(SubmissionsCog(bot), override=True)


# pretty useless now i think unsure don't want to break
def findGapInIds(dict, type):
    id = f'{type}#1'
    iterable = 1
    for i in dict:
        print(i)
        if i.startswith(type):
            if id in dict.keys():
                id = f'{type}#{iterable+1}'
                print("id equals : " + id)
                iterable += 1
                continue
    return int(id[id.find('#') + 1:])


def countKeysWith(dict, type):
    dictKeys = dict.keys()
    count = 0
    for i in dictKeys:
        if i.startswith(type):
            count += 1
    return count


#@bot.on_ready()
#async def on_ready(self):
#print(f'system online logged in as {self}')
class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    dev = SlashCommandGroup(
        "dev",
        "Commands for bot development. DO NOT USE",
        default_member_permissions=discord.Permissions(administrator=True))

    @dev.command(guild_ids=[*guildids])
    async def deleteforce(self, ctx,
                          force: Option(int,
                                        "the index of the force to delete")):
        print("deletforces triggered")
        forces = db["Forces"]
        for i in forces:
            index = forces.index(i)
            if index == force:
                force = i
                name = force['Name']
                del forces[index]
                await ctx.respond(f"force deleted {name}")
                break
        else:
            await ctx.respond("no force found", ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def delkey(self, ctx, key: Option(str, 'the db key to delete')):
        del db[key]
        await ctx.respond('key has been deleted', ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def clearuser(self, ctx, user: Option(discord.Member,
                                                'the users forms to delete')):
        dataBaseKeys = [str(user.id) + "'s forms", str(user.id) + "'s data"]
        for i in dataBaseKeys:
            del db[i]
        await ctx.respond('user has been cleared', ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def getkey(self, ctx, key: Option(str, 'the key to get')):
        value = db[key]
        for i in value:
            await ctx.respond(f'key value {i}', ephemeral=True)
            
    @dev.command(guild_ids=[*guildids])
    async def getuserkey(self, ctx, owner: Option(
        discord.Member, 'returns all a users values under their form key')):
        dataBaseKey = str(owner.id) + "'s forms"
        await ctx.respond(str(db[dataBaseKey]), ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def updatekey(self, ctx, owner: Option(discord.Member,
                                                 'the users forms to update')):
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        db[dataBaseKey] = list(userForms.values())
        await ctx.respond('key should be converted', ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def allusers(self, ctx):
        users = db.keys()
        await ctx.respond(users, ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def newtest(self, ctx):
        guild = ctx.guild
        await ctx.respond(f'test worked, guild: {guild}', ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def listforces(self, ctx):
        print("listForces triggerd")
        forces = db['Forces']
        message = ''
        for i in forces:
            message += f"\n{i}"
        await ctx.respond(f'{message}', ephemeral=True)

    @dev.command(guild_ids=[*guildids])
    async def deleteuserdata(self, ctx,
                             user: Option(discord.Member,
                                          'the users forms to delete')):
        userDataKey = f"{user.id}'s data'"
        try:
            del db[userDataKey]
            await ctx.respond('user has been cleared', ephemeral=True)
        except:
            await ctx.respond('Something has gone wrong', ephemeral=True)


setup(bot)

try:
    bot.run(token)
except:
    os.system("kill 1")
    os.system("pip install py-cord")

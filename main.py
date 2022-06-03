import keepalive
import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
import os
from replit import db
from force_commands import ForceCommands
from form_commands import FormCommands
from shared import guildIds, adminRoles, validation
keepalive.keep_alive()
bot = discord.Bot()
token = os.environ['TOKEN']
guildids = guildIds



def setup(bot):
    bot.add_cog(Dev(bot), override=True)
    bot.add_cog(FormCommands(bot), override=True)
    bot.add_cog(ForceCommands(bot), override=True)



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
    dev = SlashCommandGroup("dev", "Commands for bot development. DO NOT USE", default_member_permissions=discord.Permissions(administrator=True))
    @dev.command(guild_ids=[*guildids])
    async def delkey(self, ctx, key: Option(str,'the users forms to delete')):
        del db[key]
        await ctx.respond('key has been deleted', ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def clearuser(self, ctx, user: Option(discord.Member,'the users forms to delete')):
        dataBaseKey = str(user.id) + "'s forms"
        del db[dataBaseKey]
        await ctx.respond('user has been cleared', ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def getkey(self, ctx, owner: Option(discord.Member,'returns all a users values under their form key')):
        dataBaseKey = str(owner.id) + "'s forms"
        await ctx.respond(str(db[dataBaseKey]), ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def updatekey(self, ctx, owner: Option(discord.Member,'the users forms to update')):
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

#bot.add_application_command(form)
#bot.add_application_command(dev)
#bot.add_application_command(force)

setup(bot)

bot.run(token)

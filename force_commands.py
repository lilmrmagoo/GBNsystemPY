import discord
from discord.commands import permissions, SlashCommandGroup, Option
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion
guildids = guildIds
    
class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    PermID = "Owner"
    PermTYPE = 1
    force = SlashCommandGroup('force', 'commands to edit or create forces.'#, 
        #permissions=[
                   #permissions.CommandPermission(id=PermID, type=PermTYPE, permission=True)]
    )

    @force.command(guild_ids=[*guildids], description='a test command')
    async def hellotester(self, ctx):
        await ctx.respond("Hello, this is a slash subcommand from a cog!")
    @force.command(guild_ids=[*guildids], description='Create a Force')
    async def create(self, ctx,
        name: Option(str,"the name of the force", required=True),
        colour: Option(str, "the colour associated with the force in hexademical form ex: ffffff would be white"),
        googledoc: Option(str, "the link to the forces google doc"),
        leader: Option(discord.member, "The leader of the force")
    ):
        if leader == None:
            leader = ctx.author
        if colour == None:
            colour == "ffffff"
        elif not validation.validHexColor(colour):
            await ctx.respond("invalid colour given please use colours in hex value ex: #19778a")
        if validation.doesKeyExist("Forces"):
            Forces = db["Forces"] 
            Forces.append({
                "Name": name,
                "Colour": conversion.hexToRGB(colour),
                "Link": googledoc,
                "Leader": leader.id,
                "Ranking": 0,
                "Desc": " ",
                "Image": " "
                
            })
            db["Forces"] = Forces
        else:
            newForce = {
                "Name": name,
                "Colour": conversion.hexToRGB(colour),
                "Link": googledoc,
                "Leader": leader.id,
                "Ranking": 0,
                "Desc": " ",
                "Image": " "
                
            }
            db["Forces"] = [newForce]
        await ctx.respond(f"{name} has been created!")

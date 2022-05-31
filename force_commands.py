import discord
from discord.commands import SlashCommandGroup, Option, CommandPermission
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion
guildids = guildIds
    
class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    force = SlashCommandGroup('force', 'commands to edit or create forces.', permissions=[CommandPermission("owner", 2, True)],)

    @force.command(guild_ids=[*guildids], description='Create a Force')
    async def create(self, ctx,
        name: Option(str,"the name of the force", required=True),
        colour: Option(str, "the colour associated with the force in hexademical form ex: ffffff would be white"),
        googledoc: Option(str, "the link to the forces google doc"),
        leader: Option(discord.Member, "the leader of the force leave blank if it is you", required=False,default=None)
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
                "Members": 1,
                "Desc": " ",
                "Image": " "
                
            })
            db["Forces"] = Forces
            await ctx.guild.add_role()
        else:
            newForce = {
                "Name": name,
                "Colour": conversion.hexToRGB(colour),
                "Link": googledoc,
                "Leader": leader.id,
                "Ranking": 0,
                "Members": 1,
                "Desc": " ",
                "Image": " "
                
            }
            db["Forces"] = [newForce]
        await ctx.respond(f"{name} has been created!")

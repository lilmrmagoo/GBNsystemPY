import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion
guildids = guildIds
    
class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    force = SlashCommandGroup('force', 'commands to edit or create forces.', default_member_permissions=discord.Permissions(administrator=True))

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
                "Link": googledoc,
                "Leader": leader.id,
                "Desc": " ",
                "Image": " ",
                "Colour": colour,
                "Ranking": 0,
                "Members": 1
                
            })
            db["Forces"] = Forces
            role = await ctx.guild.create_role(name=name, color=int(colour,16),reason="new force role")
            await leader.add_roles(role)
            await ctx.respond(f"{name} has been created!")
            
        else:
            newForce = {
                "Name": name,
                "Link": googledoc,
                "Leader": leader.id,
                "Desc": " ",
                "Image": " ",
                "Colour": colour,
                "Ranking": 0,
                "Members": 1
                
            }
            db["Forces"] = [newForce]
            role = await ctx.guild.create_role(name=name, color=int(colour,16),reason="new force role")
            await leader.add_roles(role)
            await ctx.respond(f"{name} has been created!")

    @force.command(guild_ids=[*guildids], description="get the info for a force")
    async def get(
        self, ctx, 
        force: Option(str,'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=True)
    ):
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            for i in forces:
                if i['Name'].casefold().startswith(force.casefold()):
                    owner = await ctx.guild.fetch_member(i['Leader'])
                    desc = i['Desc']
                    embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                    embed.add_field(name='Leader', value=owner, inline=True)
                    embed.add_field(name='Member Count', value=i['Members'], inline=True)
                    embed.set_thumbnail(url=i['Image'])
                    embed = validation.addFieldsToEmbed(i, embed)
                    await ctx.respond(embed=embed,ephemeral=not public)
                    break
                elif forces.index(i)+1 == len(forces):
                    await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
                    break
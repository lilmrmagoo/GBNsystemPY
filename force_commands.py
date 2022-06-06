import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion, adminRoles
guildids = guildIds

def checkDupeName(name, list):
    dups = False
    for i in list:
        if i["Name"] == name:
            dups = True
    return dups
        


class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    force = SlashCommandGroup('force', 'commands to edit or create forces.', default_member_permissions=discord.Permissions(administrator=True))

    @force.command(guild_ids=[*guildids], description='Create a Force')
    async def create(self, ctx,
        name: Option(str,"the name of the force", required=True),
        googledoc: Option(str, "the link to the forces google doc"),
        colour: Option(str, "the colour associated with the force in hexademical form ex: ffffff would be white", default='ffffff'),
        leader: Option(discord.Member, "the leader of the force leave blank if it is you", required=False,default=None)
    ):
        if leader == None:
            leader = ctx.author
        if not validation.validHexColor(colour):
            await ctx.respond("invalid colour given please use colours in hex value ex: #19778a")
            return
        if validation.doesKeyExist("Forces"):
            
            forces = db["Forces"] 
            if checkDupeName(name, forces):
                await ctx.respond(f'A force with the name {name} already exists please chose another name.', ephemeral=True)
            else:
                forceDict ={
                    "Name": name,
                    "Link": googledoc,
                    "Leader": leader.id,
                    "Desc": " ",
                    "Image": " ",
                    "Colour": colour.strip('#'),
                    "Ranking": 0,
                    "Members": 1,
                    "RoleID": 0
                    
                }
                role = await ctx.guild.create_role(name=name, color=int(colour.strip('#'),16),reason="new force role")
                await leader.add_roles(role)
                forceDict["RoleID"] = role.id
                forces.append(forceDict)
                db["Forces"] = forces
                await ctx.respond(f"{name} has been created!")
            
        else:
            newForce = {
                "Name": name,
                "Link": googledoc,
                "Leader": leader.id,
                "Desc": " ",
                "Image": " ",
                "Colour": colour.strip('#'),
                "Ranking": 0,
                "Members": 1,
                "RoleID": 0
            }

            role = await ctx.guild.create_role(name=name, color=int(colour,16),reason="new force role")
            await leader.add_roles(role)
            newForce["RoleID"] = role.id
            db["Forces"] = [newForce]
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
        else: 
            await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
    @force.command(guild_ids=[*guildids], description="get the info for a force")
    async def edit(
        self, ctx, 
        force: Option(str,'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
        inputfield: Option(str,'the data of the force you want to change',choices=["Name","Link","Desc","Image","Leader","Colour"], required=True),
        inputdata: Option(str,'the new data for the inputfield, like the new name or color', required=True),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            for i in forces:
                if i['Name'].casefold().startswith(force.casefold()):
                    if i['Leader'] == ctx.author.id or validation.userHasRole(ctx.author, adminRoles):
                        guild = ctx.guild
                        role = guild.get_role(i['RoleID'])
                        if inputfield == 'Leader':
                            inputdata = int(inputdata)
                            try:  member= await ctx.guild.fetch_member(inputdata)
                            except: 
                                await ctx.respond('please input a valid user id', ephemeral=not public)
                                return
                            await member.add_roles(role)
                        elif inputfield == 'Colour':
                            if validation.validHexColor(inputdata):
                                 await role.edit(colour=int(inputdata.strip('#'),16))
                            else:
                                await ctx.respond("invalid colour given please use colours in hex value ex: #19778a", ephemeral=not public)
                                return
                        elif inputfield == 'Name':
                            await role.edit(name=inputdata)
                        index= forces.index(i)
                        forces[index][inputfield] = inputdata
                        await ctx.respond(f'{inputfield} changed to {inputdata} on {i["Name"]}',ephemeral=not public)
                        break
                    else:
                        ctx.respond("You do not have permission to edit someone else's forms.",ephemeral=True)
                        return
                elif forces.index(i)+1 == len(forces):
                    await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
                    break
        else: 
            await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
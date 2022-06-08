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
                    "MemberCount": 1,
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
                "MemberCount": 1,
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
            forceFound = False
            for i in forces:
                if i['Name'].casefold().startswith(force.casefold()):
                    owner = await ctx.guild.fetch_member(i['Leader'])
                    desc = i['Desc']
                    embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                    embed.add_field(name='Leader', value=owner, inline=True)
                    embed.add_field(name='Member Count', value=i['MemberCount'], inline=True)
                    embed.set_thumbnail(url=i['Image'])
                    embed = validation.addFieldsToEmbed(i, embed)
                    await ctx.respond(embed=embed,ephemeral=not public)
                    forceFound =True
                    break
            if not forceFound: 
                await ctx.respond(f"no force found with name {force}")
    @force.command(guild_ids=[*guildids], description="edit the info of a force")
    async def edit(
        self, ctx, 
        force: Option(str,'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
        inputfield: Option(str,'the data of the force you want to change',choices=["Name","Link","Desc","Image","Leader","Colour"], required=True),
        inputdata: Option(str,'the new data for the inputfield, like the new name or color', required=True),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            forceFound = False
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
                    else:
                        ctx.respond("You do not have permission to edit someone else's forms.",ephemeral=True)
                        return
                    forceFound = True
                    break
            if not forceFound:
                await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
        else: 
            await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
    @force.command(guild_ids=[*guildids], description="delete a force")
    async def delete(self, ctx, 
                     force: Option(str,'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
                     public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            forceFound = False
            for i in forces:
                if i['Name'].casefold().startswith(force.casefold()):
                    if i['Leader'] == ctx.author.id or validation.userHasRole(ctx.author, adminRoles):
                        role = ctx.guild.get_role(i['RoleID'])
                        await role.delete()
                        forces.remove(i)
                        await ctx.respond(f"force deleted {force}")
                    else: await ctx.respond("you do not have permision to delete someone else's force", ephemeral= not public)
                    forceFound = True
            if not forceFound:
                await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
        else:  await ctx.respond(f'no force found with the name: {force}', ephemeral=True)

    @force.command(guild_ids=[*guildids], description="join a force")
    async def join(self, ctx,
                     force: Option(str,'the force you want to join. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
                     public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        forceFound = False
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            for i in forces:
                if i['Name'].casefold().startswith(force.casefold()):
                    role = ctx.guild.get_role(i['RoleID'])
                    name = i['Name']
                    await ctx.author.add_roles(role)
                    i['MemberCount'] += 1
                    await ctx.respond(f'You have been added to the force {name}')
                    forceFound = True
                    break
        if not forceFound:
            await ctx.respond(f'no force found with the name: {force}')
    @force.command(guild_ids=[*guildids], description="join a force")
    async def leave(self, ctx,
                     force: Option(str,'the force you want to leave. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
                     public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        forceFound = False
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            for i in forces:
                if i['Name'].casefold().startswith(force.casefold()):
                    role = ctx.guild.get_role(i['RoleID'])
                    name = i['Name']
                    forceFound = True
                    if validation.userHasRole(ctx.author, role.name) and ctx.author.id!=i['Leader'] :
                        await ctx.author.remove_roles(role)
                        i['MemberCount'] -= 1
                        await ctx.respond(f'You have left the force {name}')
                    else: 
                        await ctx.respond(f'you are not in the force {name} and or are the leader and can not leave the force.')
                    break
        if not forceFound:
            await ctx.respond(f'no force found with the name: {force}')
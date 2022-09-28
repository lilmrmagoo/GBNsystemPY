import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from discord.ui import Modal, InputText, Button, View
from replit import db
from shared import guildIds, validation, conversion, adminRoles
guildids = guildIds

def createPageView(dict):
    view = PageView(timeout=300.0,disable_on_timeout=True)
    numofPages = 0
    if "Members" in dict.keys():
        view.add_item(FormNavButton(form=dict,label="Members",page="characters"))
        numofPages+=1
    if numofPages>0:
        view.add_item(FormNavButton(form=dict,label="Info",page="info"))
    return view
def createMemberEmbed(dict):
    members = sortMembersByRole(dict['Members'])
    forceName = dict['Name']
    embed=discord.Embed(title=f"{forceName}", url=dict['Link'],color=0x2ca098)
    for i in members.keys():
        list = []
        for j in members[i]:
            doc = members[i][j]
            list.append(f"[{j}]({doc})")
        finalString = '\n'.join(list)
        embed.add_field(name=f"{i}s",value=finalString,inline=False)
    return embed
def createEmbed(dict, owner):
    desc = dict['Desc']
    inlink = dict['Link']
    inimage = dict['Image']
    link = None
    image = None
    if validation.validGoogleDoc(inlink) or validation.validDiscordLink(inlink):
        link = inlink
    else:
        print(f'{inlink} is an invalid link')
        link = 'https://discord.com/channels/479493485037355022/591348299752013837/917927502872215552'
    if inimage.startswith('https') or inimage.startswith('http'):
        image = inimage
    else:
        image ='https://cdn.discordapp.com/avatars/826265731930128394/ce7d79e6332e54a9a394b42cb182ddf7.png?size=4096'
    embed= discord.Embed(title=dict['Name'],url=link, description=desc, color=0x2ca098)
    embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
    embed.set_thumbnail(url=image)
    embed.add_field(name='Leader', value=owner, inline=True)
    embed.add_field(name='Member Count', value=dict['MemberCount'], inline=True)
    embed = validation.addFieldsToEmbed(dict, embed)
    return embed

def sortMembersByRole(members):
    roles = []
    sorted = {}
    for i in members:
        role = i['Role']
        name = i['Name']
        doc = i['Doc']
        sorted = {}
        if role in roles:
            sorted[role][name]=doc
        else:
            roles.append(role)
            sorted[role] = {name:doc}
    return sorted
def checkDupeName(name, list):
    dups = False
    for i in list:
        if i["Name"] == name:
            dups = True
    return dups
        
#class NestModal(Modal):
    #def __init__(self,*args,**kwargs) -> None:

class PageView(View):
    def __init__(self, timeout=300,disable_on_timeout=True):
        super().__init__(timeout=timeout)
        self.disable_on_timeout=disable_on_timeout
    async def on_timeout(self):
        await self.interaction.edit_original_message(view=None)
        self.disable_all_items()
        self.clear_items()
    def set_interaction(self, interaction):
        self.interaction = interaction
class FormNavButton(Button):
    def __init__(self,page=None,form=None,label=None):
        super().__init__(label=label,style=discord.ButtonStyle.primary)
        self.page = page
        self.form = form
    async def callback(self, interaction: discord.Interaction):
        form = self.form
        userID = form["Leader"]
        guild = interaction.guild
        user = await guild.fetch_member(userID)
        print(f"guild: {guild} user: {user} userID: {userID}")
        response = interaction.response
        if self.page.casefold() == "characters":
            await response.edit_message(embed=createMemberEmbed(form))
        if self.page.casefold() == "info":
            await response.edit_message(embed=createEmbed(form,user))

class ForceModal(Modal):
    def __init__(self, oldValues=None, edit=False, *args, **kwargs) -> None:
        self.edit = edit
        if not edit:
            super().__init__(*args, **kwargs)
            self.add_item(InputText(label="Name", placeholder="Put the name here", style= discord.InputTextStyle.short,row=0))
            self.add_item(InputText(label="Description", placeholder="describe the form here", style=discord.InputTextStyle.long,row=1))
            self.add_item(InputText(label="Image", placeholder="put a link to an image here", style=discord.InputTextStyle.short,row = 2 ,required=False))
            self.add_item(InputText(label="Document", placeholder="put a link to a google doc or discord message link here", style=discord.InputTextStyle.short, row= 3))
            self.add_item(InputText(label="Color", placeholder="put a the colour associated with the force in hexademical form ex: ffffff would be white",value="ffffff",min_length=6,max_length=6, style=discord.InputTextStyle.short, row= 4))
        elif edit:
            super().__init__(*args, **kwargs)
            self.add_item(InputText(label="Name", placeholder="Put the name here", style= discord.InputTextStyle.short,row=0,value=oldValues['Name']))
            self.add_item(InputText(label="Description", placeholder="describe the form here", style=discord.InputTextStyle.long,row=1,value=oldValues['Desc']))
            self.add_item(InputText(label="Image", placeholder="put a link to an image here", style=discord.InputTextStyle.short,row = 2 ,required=False,value=oldValues['Image']))
            self.add_item(InputText(label="Document", placeholder="put a link to a google doc or discord message link here", style=discord.InputTextStyle.short, row= 3, value=oldValues['Link']))
            self.add_item(InputText(label="Color", placeholder="put a the colour associated with the force in hexademical form ex: ffffff would be white",value=oldValues['Colour'],min_length=6,max_length=6, style=discord.InputTextStyle.short, row= 4))
            self.oldName = oldValues['Name']
            self.oldRole = oldValues['RoleID']
    async def callback(self, interaction: discord.Interaction):
        googledoc = self.children[3].value
        desc = self.children[1].value
        image = self.children[2].value
        name = self.children[0].value
        colour = self.children[4].value
        leader = interaction.user
        newForce = {
            "Name": name,
            "Link": googledoc,
            "Leader": leader.id,
            "Desc": desc,
            "Image": image,
            "Colour": colour.strip('#'),
            "Ranking": 0,
            "MemberCount": 1,
            "Members": [],
            "RoleID": 0
        }

        if self.edit:
            forces = db["Forces"] 
            forceFound=False
            for i in forces:
                if i['Name'] == self.oldName:
                    forceFound == True
                    index = forces.index(i)
                    role = interaction.guild.get_role(self.oldRole)
                    await role.edit(name=name,color=int(colour.strip('#'),16))
                    newForce['RoleID'] = role.id
                    forces[index] = newForce
                    embed = createEmbed(newForce,leader)
                    await interaction.response.send_message(f"{name} has been edited!", embed=embed,ephemeral=True)
            if forceFound == False:
                await interaction.response.send_message(f"force {name} cannot be found.", embed=embed,ephemeral=True)
        else:
            if validation.doesKeyExist("Forces"):
                forces = db["Forces"] 
                if checkDupeName(name, forces):
                    await interaction.response.send_message(f'A force with the name {name} already exists please chose another name.', ephemeral=True)
                else:
                    role = await interaction.guild.create_role(name=name, color=int(colour.strip('#'),16),reason="new force role")
                    await leader.add_roles(role)
                    newForce["RoleID"] = role.id
                    forces.append(newForce)
                    db["Forces"] = forces
            
            else:
                role = await interaction.guild.create_role(name=name, color=int(colour,16),reason="new force role")
                await leader.add_roles(role)
                newForce["RoleID"] = role.id
                db["Forces"] = [newForce]
            forces = db["Forces"]
    
            embed = createEmbed(newForce,leader)
            await interaction.response.send_message(f"{name} has been created!", embed=embed,ephemeral=True)

class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    force = SlashCommandGroup('force', 'commands to edit or create forces.', default_member_permissions=discord.Permissions(administrator=True))
    memberCommandGroup = force.create_subgroup('member','commands to add characters as members to forces')
    
    @force.command(guild_ids=[*guildids], description='Create a Force')
    async def create(self,ctx):
        print('command create force activated')
        modal = ForceModal(title=f"Create a Force ")
        await ctx.send_modal(modal)

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
                    embed=createEmbed(i,owner)
                    view = createPageView(i)
                    interaction = await ctx.respond(embed=embed,ephemeral=not public, view=view)
                    view.set_interaction(interaction)
                    forceFound =True
                    break
            if not forceFound: 
                await ctx.respond(f"no force found with name {force}")
    @force.command(guild_ids=[*guildids], description="edit the info of a force")
    async def edit(
        self, ctx, 
        force: Option(str,'the force you want to edit. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        forces = db['Forces'] 
        for i in forces:
            if i['Name'].casefold().startswith(force.casefold()):
                if ctx.author.id == i['Leader']:
                    modal = ForceModal(title=f"Edit {i['Name']}.",edit=True,oldValues=i)
                    await ctx.send_modal(modal)
                else:
                    ctx.respond('you are not the leader of the force',ephemeral=True)
    
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
                        if role != None: await role.delete()
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
                        await ctx.respond(f'You have left the force {name}')
                    else: 
                        await ctx.respond(f'you are not in the force {name} and or are the leader and can not leave the force.')
                    break
        if not forceFound:
            await ctx.respond(f'no force found with the name: {force}')
    @memberCommandGroup.command(guild_ids=[*guildids], description="add a member to a force")
    async def add(self, ctx, 
                  force: Option(str,"the force to add the member to", required=True),
                  member: Option(str, "the name of the member",required=True),
                  role: Option(str, "the role of the member, Ex: officer, junior etc", required=True),
                  doc: Option(str, 'A link for the character', required=True)
    ):
        forceFound = False
        for i in db['Forces']:
            if i['Name'].casefold().startswith(force.casefold()):
                forceFound = True
                if 'Members' not in i.keys():
                    i['Members'] = []
                members = i['Members']    
                dict = {"Name":member,"Role":role,"Doc":doc}
                if not members == None:
                    members.append(dict)
                else: 
                    members = [dict]
                i['Members'] = members
                await ctx.respond(f"{role} {member} has been added to {i['Name']}")
                
                break
        if not forceFound:
            await ctx.respond(f"no force found with the name {force}",ephemeral=True)
    @memberCommandGroup.command(guild_ids=[*guildids], description="list the members in a force")
    async def list(self,ctx, 
                   force: Option(str,"the force to add the member to", required=True),
                   public: Option(bool,"Will show the result to only you if false", default=True)
    ):
        forceFound = False
        for i in db['Forces']:
            if i['Name'].casefold().startswith(force.casefold()):
                forceFound = True
                embed = createMemberEmbed(i)
                await ctx.respond(embed=embed,ephemeral=not public)
        if not forceFound:
            await ctx.respond(f"no force found with the name {force}",ephemeral=True)
    @memberCommandGroup.command(guild_ids=[*guildids], description="remove a member from a force")
    async def remove(self,ctx, 
                     force: Option(str,"the force to remove the memebr from.", required=True),
                     member: Option(str,"the member to remove from the force", required=True),
                     public: Option(bool,"whether or not to make te response public", required=False)
                     
    ):
        forceFound = False
        memberFound = False
        for i in db['Forces']:
            if i['Name'].casefold().startswith(force.casefold()):
                forceFound = True
                forceName = i['Name']
                for j in i['Members']:
                    if j['Name'].casefold().startswith(member.casefold()):
                        memberFound = True
                        i["Members"].remove(j)
                        await ctx.respond(f"{j['Name']} removed from {forceName}")
                        break
                break
        if not forceFound:
            await ctx.respond(f"no force found with the name {force}",ephemeral=True)
        if not memberFound:
            await ctx.respond(f"{member} is not a member of {force}",ephemeral=True)
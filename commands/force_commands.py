import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from discord.ui import Modal, InputText, Button, View
from replit import db
from shared import guildIds, validation, conversion, adminRoles
guildids = guildIds


class Force:
    def __init__(self, Name: str,Link: str,Leader: int,
                Desc: str = None,
                Image: str = None,
                Colour: str = None,
                Ranking: int = 0,
                MemberCount: int = 0,
                Members: dict = [],
                RoleID: int = 0
    ):
        #loops through arguments and sets them as attributes of the class
        args = locals()
        for k,v in args.items():
            if k == "self": continue
            setattr(self,k,v)
    #writen by open ai's chatgpt ai converts Force to dict for database purposes.
    def to_dict(self):
      return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr))and not attr.startswith("__") and attr !="self"}
    #creates the members page embed for the force
    def createMemberEmbed(self):
        members = sortMembersByRole(self.Members)
        forceName = self.Name
        embed=discord.Embed(title=f"{forceName}", url=self.Link,color=0x2ca098)
        for i in members.keys():
            list = []
            for j in members[i]:
                doc = members[i][j]
                list.append(f"[{j}]({doc})")
            finalString = '\n'.join(list)
            embed.add_field(name=f"{i}s",value=finalString,inline=False)
        return embed
    #creates the main page emebed for the force
    def createEmbed(self, owner):
        inlink = self.Link
        inimage = self.Image
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
        embed= discord.Embed(title=self.Name,url=link, description=self.Desc, color=0x2ca098)
        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
        embed.set_thumbnail(url=image)
        embed.add_field(name='Leader', value=owner, inline=True)
        embed.add_field(name='Member Count', value=self.MemberCount, inline=True)
        embed = validation.addFieldsToEmbed(self.to_dict(), embed)
        return embed
    #saves the force to the database
    def save(self):
        db["Forces"][self.Name] = self.to_dict()
    #searches the database for the force by name then returns the object
    @staticmethod
    def searchDatabase(name, strict = False):
        if not strict:
            for i in db["Forces"]: 
                if i["Name"].casefold().startswith(name.casefold()): 
                    return Force(**i)
            else:
                return None
        else:
            for i in db["Forces"]: 
                if i["Name"] == name: return Force(**i)
            else:
                return None


def createPageView(dict):
    view = PageView(timeout=300.0,disable_on_timeout=True)
    numofPages = 0
    if "Members" in dict.keys():
        view.add_item(FormNavButton(form=dict,label="Members",page="characters"))
        numofPages+=1
    if numofPages>0:
        view.add_item(FormNavButton(form=dict,label="Info",page="info"))
    return view
# def createMemberEmbed(dict):
#     members = sortMembersByRole(dict['Members'])
#     forceName = dict['Name']
#     embed=discord.Embed(title=f"{forceName}", url=dict['Link'],color=0x2ca098)
#     for i in members.keys():
#         list = []
#         for j in members[i]:
#             doc = members[i][j]
#             list.append(f"[{j}]({doc})")
#         finalString = '\n'.join(list)
#         embed.add_field(name=f"{i}s",value=finalString,inline=False)
#     return embed
# def createEmbed(dict, owner):
#     desc = dict['Desc']
#     inlink = dict['Link']
#     inimage = dict['Image']
#     link = None
#     image = None
#     if validation.validGoogleDoc(inlink) or validation.validDiscordLink(inlink):
#         link = inlink
#     else:
#         print(f'{inlink} is an invalid link')
#         link = 'https://discord.com/channels/479493485037355022/591348299752013837/917927502872215552'
#     if inimage.startswith('https') or inimage.startswith('http'):
#         image = inimage
#     else:
#         image ='https://cdn.discordapp.com/avatars/826265731930128394/ce7d79e6332e54a9a394b42cb182ddf7.png?size=4096'
#     embed= discord.Embed(title=dict['Name'],url=link, description=desc, color=0x2ca098)
#     embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
#     embed.set_thumbnail(url=image)
#     embed.add_field(name='Leader', value=owner, inline=True)
#     embed.add_field(name='Member Count', value=dict['MemberCount'], inline=True)
#     embed = validation.addFieldsToEmbed(dict, embed)
#     return embed

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
    async def on_timeout(self):
        await self.interaction.edit_original_response(view=None)
        self.disable_all_items()
        self.clear_items()
    def set_interaction(self, interaction):
        self.interaction = interaction 
class FormNavButton(Button):
    def __init__(self,page=None,form=None,label=None):
        super().__init__(label=label,style=discord.ButtonStyle.primary)
        self.page = page
        self.form = Force(**form)
    async def callback(self, interaction: discord.Interaction):
        force = self.form
        userID = force.Leader
        guild = interaction.guild
        user = await guild.fetch_member(userID)
        print(f"guild: {guild} user: {user} userID: {userID}")
        response = interaction.response
        if self.page.casefold() == "characters":
            await response.edit_message(embed=force.createMemberEmbed())
        if self.page.casefold() == "info":
            await response.edit_message(embed=force.createEmbed(user))

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
        newForce = Force(
            Name= name,
            Link= googledoc,
            Leader= leader.id,
            Desc= desc,
            Image= image,
            Colour= colour.strip('#'),
            MemberCount= 1,
        )

        if self.edit:
            forces = db["Forces"] 
            dbForce = Force.searchDatabase(self.oldName, strict=True)
            if dbForce != None:
                    index = forces.index(dbForce.to_dict())
                    role = interaction.guild.get_role(self.oldRole)
                    await role.edit(name=name,color=int(colour.strip('#'),16))
                    newForce.RoleID = role.id
                    forces[index] = newForce.to_dict()
                    embed = newForce.createEmbed(leader)
                    await interaction.response.send_message(f"{name} has been edited!", embed=embed,ephemeral=True)
            else:
                await interaction.response.send_message(f"force {name} cannot be found.", embed=embed,ephemeral=True)
        else:
            if validation.doesKeyExist("Forces"):
                forces = db["Forces"] 
                if checkDupeName(name, forces):
                    await interaction.response.send_message(f'A force with the name {name} already exists please chose another name.', ephemeral=True)
                else:
                    role = await interaction.guild.create_role(name=name, color=int(colour.strip('#'),16),reason="new force role")
                    await leader.add_roles(role)
                    newForce.RoleID = role.id
                    forces.append(newForce.to_dict())
                    db["Forces"] = forces
            
            else:
                role = await interaction.guild.create_role(name=name, color=int(colour,16),reason="new force role")
                await leader.add_roles(role)
                newForce.RoleID = role.id
                db["Forces"] = [newForce.to_dict()]
            forces = db["Forces"]
    
            embed = newForce.createEmbed(leader)
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
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                owner = await ctx.guild.fetch_member(dbForce.Leader)
                embed=dbForce.createEmbed(owner)
                view = createPageView(dbForce.to_dict())
                interaction = await ctx.respond(embed=embed,ephemeral=not public, view=view)
                view.set_interaction(interaction)
            else: 
                await ctx.respond(f"no force found with name {force}")
    @force.command(guild_ids=[*guildids], description="edit the info of a force")
    async def edit(
        self, ctx, 
        force: Option(str,'the force you want to edit. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            if ctx.author.id == dbForce.Leader:
                modal = ForceModal(title=f"Edit {dbForce.Name}.",edit=True,oldValues=dbForce.to_dict())
                await ctx.send_modal(modal)
            else:
                ctx.respond('you are not the leader of the force',ephemeral=True)
        else:
            ctx.respond(f"no force found with the name {dbForce.Name}",ephemeral=True)
    
    @force.command(guild_ids=[*guildids], description="delete a force")
    async def delete(self, ctx, 
                     force: Option(str,'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
                     public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                if dbForce['Leader'] == ctx.author.id or validation.userHasRole(ctx.author, adminRoles):
                    role = ctx.guild.get_role(dbForce.RoleID)
                    if role != None: await role.delete()
                    forces.remove(dbForce.to_dict())
                    await ctx.respond(f"force deleted {dbForce.Name}")
                else: await ctx.respond("you do not have permision to delete someone else's force", ephemeral= not public)
            else:
                await ctx.respond(f'no force found with the name: {force}', ephemeral=True)
        else:  await ctx.respond(f'no forces found with the name: {force}', ephemeral=True)

    @force.command(guild_ids=[*guildids], description="join a force")
    async def join(self, ctx,
                     force: Option(str,'the force you want to join. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
                     public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        if validation.doesKeyExist("Forces"):
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                role = ctx.guild.get_role(dbForce.RoleID)
                await ctx.author.add_roles(role)
                await ctx.respond(f'You have been added to the force {dbForce.Name}')
            else:
                await ctx.respond(f'no force found with the name: {force}')
        else:  await ctx.respond(f'no forces found with the name: {force}', ephemeral=True)
    @force.command(guild_ids=[*guildids], description="join a force")
    async def leave(self, ctx,
                     force: Option(str,'the force you want to leave. ex: \'build divers\' or \'pizza grubbers\'' ,required=True),
                     public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=False)
    ):
        if validation.doesKeyExist("Forces"):
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                    role = ctx.guild.get_role(dbForce.RoleID)
                    name = dbForce.Name
                    if validation.userHasRole(ctx.author, role.name) and ctx.author.id!=dbForce.Leader:
                        await ctx.author.remove_roles(role)
                        await ctx.respond(f'You have left the force {name}')
                    else: 
                        await ctx.respond(f'you are not in the force {name} and or are the leader and can not leave the force.')
            else:
                await ctx.respond(f'no force found with the name: {force}')
        else:
            await ctx.respond(f'no forces found with the name: {force}')
    @memberCommandGroup.command(guild_ids=[*guildids], description="add a member to a force")
    async def add(self, ctx, 
                  force: Option(str,"the force to add the member to", required=True),
                  member: Option(str, "the name of the member",required=True),
                  role: Option(str, "the role of the member, Ex: officer, junior etc", required=True),
                  doc: Option(str, 'A link for the character', required=True)
    ):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            members = dbForce.Members    
            dict = {"Name":member,"Role":role,"Doc":doc}
            if members != None:
                members.append(dict)
            else: 
                members = [dict]
            dbForce.save()
            await ctx.respond(f"{role} {member} has been added to {dbForce.Name}")
        else:
            await ctx.respond(f"no force found with the name {force}",ephemeral=True)
    @memberCommandGroup.command(guild_ids=[*guildids], description="list the members in a force")
    async def list(self,ctx, 
                   force: Option(str,"the force to add the member to", required=True),
                   public: Option(bool,"Will show the result to only you if false", default=True)
    ):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            embed = dbForce.createMemberEmbed()
            await ctx.respond(embed=embed,ephemeral=not public)
        else:
            await ctx.respond(f"no force found with the name {force}",ephemeral=True)
    @memberCommandGroup.command(guild_ids=[*guildids], description="remove a member from a force")
    async def remove(self,ctx, 
                     force: Option(str,"the force to remove the memebr from.", required=True),
                     member: Option(str,"the member to remove from the force", required=True),
                     public: Option(bool,"whether or not to make the response public", required=False)
                     
    ):
        memberFound = False
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            forceName = dbForce.Name
            for i in dbForce.Members:
                if i['Name'].casefold().startswith(member.casefold()):
                    memberFound = True
                    dbForce.Members.remove(i)
                    dbForce.save()
                    await ctx.respond(f"{i['Name']} removed from {forceName}")
                    break
        else:
            await ctx.respond(f"no force found with the name {force}",ephemeral=True)
        if not memberFound:
            await ctx.respond(f"{member} is not a member of {force}",ephemeral=True)
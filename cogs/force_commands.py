import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from discord.ui import Modal, InputText, Button
from shared import guildIds, validation, adminRoles, PageView, ImageGeneration
from classes.force import Force
from classes.force_nest import ForceNest
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import textwrap
import math

guildids = guildIds


def checkDupeName(name, list):
    dups = False
    for i in list:
        if i["Name"] == name:
            dups = True
    return dups




class ForceNavButton(Button):
    def __init__(self, label, page, force: Force, display_type=None):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.page = page
        self.force = force
        self.display_type = display_type

    async def callback(self, interaction: discord.Interaction):
        force = self.force
        userID = force.Leader
        guild = interaction.guild
        user = await guild.fetch_member(userID)
        print(f"guild: {guild} user: {user} userID: {userID}")
        response = interaction.response
        if self.display_type == "Image":
            if self.page.casefold() == "characters":
                await response.edit_message(file=force.createMemberScreen(),
                                            attachments=[])
            if self.page.casefold() == "info":
                await response.edit_message(file=force.createInfoScreen(),
                                            attachments=[])
        else:
            if self.page.casefold() == "characters":
                await response.edit_message(embed=force.createMemberEmbed())
            if self.page.casefold() == "info":
                await response.edit_message(embed=force.createEmbed(user))
            if self.page.casefold() == "nest":
                await response.edit_message(
                    embed=force.getForceNest().createEmbed())


class ForceNestModal(Modal):
    def __init__(self,
                 oldValues: ForceNest = None,
                 edit=False,
                 force: Force = None,
                 size: str = "tiny",
                 *args,
                 **kwargs) -> None:
        self.edit = edit
        self.force = force
        self.size = size
        if not edit:
            super().__init__(*args, **kwargs)
            self.add_item(
                InputText(label="Name",
                          placeholder="Put the name here",
                          style=discord.InputTextStyle.short,
                          row=0))
            self.add_item(
                InputText(label="Description",
                          placeholder="describe the force nest here",
                          style=discord.InputTextStyle.long,
                          row=1,
                          max_length=1800))
            self.add_item(
                InputText(label="Image",
                          placeholder="put a link to an image here",
                          style=discord.InputTextStyle.short,
                          row=2,
                          required=False))
            self.add_item(
                InputText(
                    label="Document",
                    placeholder=
                    "put a link to a google doc or discord message link here",
                    style=discord.InputTextStyle.short,
                    row=3))
        elif edit:
            self.add_item(
                InputText(label="Name",
                          placeholder="Put the name here",
                          style=discord.InputTextStyle.short,
                          row=0,
                          value=oldValues.Name))
            self.add_item(
                InputText(label="Description",
                          placeholder="describe the force nest here",
                          style=discord.InputTextStyle.long,
                          row=1,
                          max_length=1800,
                          value=oldValues.Desc))
            self.add_item(
                InputText(label="Image",
                          placeholder="put a link to an image here",
                          style=discord.InputTextStyle.short,
                          row=2,
                          required=False,
                          value=oldValues.Image))
            self.add_item(
                InputText(
                    label="Document",
                    placeholder=
                    "put a link to a google doc or discord message link here",
                    style=discord.InputTextStyle.short,
                    row=3,
                    value=oldValues.Link))
            self.oldValues = oldValues

    async def callback(self, interaction: discord.Interaction):
        googledoc = self.children[3].value
        desc = self.children[1].value
        image = self.children[2].value
        name = self.children[0].value
        print(f"call back reached {name}, {self.edit}")
        if self.edit:
            editedForceNest = ForceNest(Name=name,
                                        Link=googledoc,
                                        Force=self.force,
                                        Desc=desc,
                                        Image=image,
                                        Size=self.size,
                                        Id=self.oldValues.Id)
            if self.oldValues != None:
                nests = db["ForceNests"]
                index = nests.index(self.oldValues.to_dict())
                nests[index] = editedForceNest
                db["ForceNests"] = nests
                embed = editedForceNest.createEmbed()
                await interaction.response.send_message(
                    f"{name} has been edited!", embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"No forcenest found: {name}", ephemeral=True)
        else:
            newForceNest = ForceNest(Name=name,
                                     Link=googledoc,
                                     Force=self.force,
                                     Desc=desc,
                                     Image=image,
                                     Size=self.size)
            if validation.doesKeyExist("ForceNests"):
                nests = db["ForceNests"]
                nests.append(newForceNest.to_dict())
                db["ForceNests"] = nests
            else:
                print("else reached")
                db["ForceNests"] = [newForceNest.to_dict()]
            self.force.NestID = newForceNest.Id
            self.force.save()
            await interaction.response.send_message(
                f"The force nest {name} has been added to the force {self.force.Name}",
                embed=newForceNest.createEmbed())


class ForceModal(Modal):
    def __init__(self, oldValues=None, edit=False, *args, **kwargs) -> None:
        self.edit = edit
        if not edit:
            super().__init__(*args, **kwargs)
            self.add_item(
                InputText(label="Name",
                          placeholder="Put the name here",
                          style=discord.InputTextStyle.short,
                          row=0))
            self.add_item(
                InputText(label="Description",
                          placeholder="describe the form here",
                          style=discord.InputTextStyle.long,
                          row=1,
                          max_length=1800))
            self.add_item(
                InputText(label="Image",
                          placeholder="put a link to an image here",
                          style=discord.InputTextStyle.short,
                          row=2,
                          required=False))
            self.add_item(
                InputText(
                    label="Document",
                    placeholder=
                    "put a link to a google doc or discord message link here",
                    style=discord.InputTextStyle.short,
                    row=3))
            self.add_item(
                InputText(
                    label="Color",
                    placeholder=
                    "put a the colour associated with the force in hexademical form ex: ffffff would be white",
                    value="ffffff",
                    min_length=6,
                    max_length=6,
                    style=discord.InputTextStyle.short,
                    row=4))
        elif edit:
            super().__init__(*args, **kwargs)
            self.add_item(
                InputText(label="Name",
                          placeholder="Put the name here",
                          style=discord.InputTextStyle.short,
                          row=0,
                          value=oldValues.Name))
            self.add_item(
                InputText(label="Description",
                          placeholder="describe the form here",
                          style=discord.InputTextStyle.long,
                          row=1,
                          value=oldValues.Desc))
            self.add_item(
                InputText(label="Image",
                          placeholder="put a link to an image here",
                          style=discord.InputTextStyle.short,
                          row=2,
                          required=False,
                          value=oldValues.Image))
            self.add_item(
                InputText(
                    label="Document",
                    placeholder=
                    "put a link to a google doc or discord message link here",
                    style=discord.InputTextStyle.short,
                    row=3,
                    value=oldValues.Link))
            self.add_item(
                InputText(
                    label="Color",
                    placeholder=
                    "put the colour associated with the force in hexademical form ex: ffffff would be white",
                    value=oldValues.Colour,
                    min_length=6,
                    max_length=6,
                    style=discord.InputTextStyle.short,
                    row=4))
            self.oldValues = oldValues

    async def callback(self, interaction: discord.Interaction):
        googledoc = self.children[3].value
        desc = self.children[1].value
        image = self.children[2].value
        name = self.children[0].value
        colour = self.children[4].value
        leader = interaction.user
        newForce = Force(Name=name,
                         Link=googledoc,
                         Leader=leader.id,
                         Desc=desc,
                         Image=image,
                         Colour=colour.strip('#'),
                         MemberCount=1,
                         ServerID=interaction.guild_id)

        if self.edit:
            forces = db["Forces"]
            dbForce = self.oldValues
            if interaction.guild_id != dbForce.ServerID:
                print("invalid server")
                await interaction.response.send_message(
                    f"{name} does not belong to this server. Please edit the force on its coressponding server",
                    ephemeral=True)
                return
            if dbForce != None:
                print(dbForce)
                print(dbForce.to_dict())
                index = forces.index(dbForce.to_dict())
                role = interaction.guild.get_role(self.oldValues.RoleID)
                await role.edit(name=name, color=int(colour.strip('#'), 16))
                newForce.RoleID = role.id
                forces[index] = newForce.to_dict()
                embed = newForce.createEmbed(leader)
                await interaction.response.send_message(
                    f"{name} has been edited!", embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"force {name} cannot be found.",
                    embed=embed,
                    ephemeral=True)
        else:
            if validation.doesKeyExist("Forces"):
                forces = db["Forces"]
                if checkDupeName(name, forces):
                    await interaction.response.send_message(
                        f'A force with the name {name} already exists please chose another name.',
                        ephemeral=True)
                else:
                    role = await interaction.guild.create_role(
                        name=name,
                        color=int(colour.strip('#'), 16),
                        reason="new force role")
                    await leader.add_roles(role)
                    newForce.RoleID = role.id
                    forces.append(newForce.to_dict())
                    db["Forces"] = forces

            else:
                role = await interaction.guild.create_role(
                    name=name, color=int(colour, 16), reason="new force role")
                await leader.add_roles(role)
                newForce.RoleID = role.id
                db["Forces"] = [newForce.to_dict()]

            embed = newForce.createEmbed(leader)
            await interaction.response.send_message(
                f"{name} has been created!", embed=embed)


class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    force = SlashCommandGroup(
        'force',
        'commands to edit or create forces.',
        default_member_permissions=discord.Permissions(administrator=True))
    memberCommandGroup = force.create_subgroup(
        'member', 'commands to add characters as members to forces')
    nestCommandGroup = force.create_subgroup(
        'nest', "Commands to add or edit a force's nest")

    @nestCommandGroup.command(guild_ids=[*guildids],
                              description='Create a Force Nest',
                              name="create")
    async def nestcreate(
        self, ctx, force: Option(str,
                                 'the force you want to add the nest to',
                                 required=True),
        size: Option(str,
                     'The size of the Force nest',
                     choices=["Tiny", 'Small', 'Meduim', 'Large'],
                     required=True)):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            print(dbForce.to_dict())
            modal = ForceNestModal(title="Create a Force Nest",
                                   force=dbForce,
                                   size=size)
            await ctx.send_modal(modal)
        else:
            await ctx.respond(f"No force found with name {force}")

    @force.command(guild_ids=[*guildids], description='Create a Force')
    async def create(self, ctx):
        print('command create force activated')
        modal = ForceModal(title="Create a Force")
        await ctx.send_modal(modal)

    @force.command(guild_ids=[*guildids],
                   description="get the info for a force")
    async def get(self, ctx, 
                  force: Option(str, 'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'',required=True), 
                  public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=True)
    ):
        if validation.doesKeyExist("Forces"):
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                owner = await ctx.guild.fetch_member(dbForce.Leader)
                embed = dbForce.createEmbed(owner)
                view = dbForce.createPageView()
                await ctx.respond(embed=embed, ephemeral=not public, view=view)
            else:
                await ctx.respond(f"no force found with name {force}")

    @force.command(guild_ids=[*guildids],
                   description="edit the info of a force")
    async def edit(self, ctx, force: Option(
        str,
        'the force you want to edit. ex: \'build divers\' or \'pizza grubbers\'',
        required=True), public: Option(
            bool,
            "makes the message only visible to you if false, True by default",
            required=False,
            default=False)):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            if ctx.author.id == dbForce.Leader:
                modal = ForceModal(title=f"Edit {dbForce.Name}.",
                                   edit=True,
                                   oldValues=dbForce)
                await ctx.send_modal(modal)
            else:
                ctx.respond('you are not the leader of the force',
                            ephemeral=True)
        else:
            ctx.respond(f"no force found with the name {dbForce.Name}",
                        ephemeral=True)

    @force.command(guild_ids=[*guildids], description="delete a force")
    async def delete(self, ctx, force: Option(
        str,
        'the force you want to get. ex: \'build divers\' or \'pizza grubbers\'',
        required=True), public: Option(
            bool,
            "makes the message only visible to you if false, True by default",
            required=False,
            default=False)):
        if validation.doesKeyExist("Forces"):
            forces = db["Forces"]
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                if dbForce.Leader == ctx.author.id or validation.userHasRole(
                        ctx.author, adminRoles):
                    role = ctx.guild.get_role(dbForce.RoleID)
                    if role != None: await role.delete()
                    forces.remove(dbForce.to_dict())
                    await ctx.respond(f"force deleted {dbForce.Name}")
                else:
                    await ctx.respond(
                        "you do not have permision to delete someone else's force",
                        ephemeral=not public)
            else:
                await ctx.respond(f'no force found with the name: {force}',
                                  ephemeral=True)
        else:
            await ctx.respond(f'no forces found with the name: {force}',
                              ephemeral=True)

    @force.command(guild_ids=[*guildids], description="join a force")
    async def join(self, ctx, force: Option(
        str,
        'the force you want to join. ex: \'build divers\' or \'pizza grubbers\'',
        required=True), public: Option(
            bool,
            "makes the message only visible to you if false, True by default",
            required=False,
            default=False)):
        if validation.doesKeyExist("Forces"):
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                role = ctx.guild.get_role(dbForce.RoleID)
                await ctx.author.add_roles(role)
                await ctx.respond(
                    f'You have been added to the force {dbForce.Name}')
            else:
                await ctx.respond(f'no force found with the name: {force}')
        else:
            await ctx.respond(f'no forces found with the name: {force}',
                              ephemeral=True)

    @force.command(guild_ids=[*guildids], description="join a force")
    async def leave(self, ctx, force: Option(
        str,
        'the force you want to leave. ex: \'build divers\' or \'pizza grubbers\'',
        required=True), public: Option(
            bool,
            "makes the message only visible to you if false, True by default",
            required=False,
            default=False)):
        if validation.doesKeyExist("Forces"):
            dbForce = Force.searchDatabase(force)
            if dbForce != None:
                role = ctx.guild.get_role(dbForce.RoleID)
                name = dbForce.Name
                if validation.userHasRole(
                        ctx.author,
                        role.name) and ctx.author.id != dbForce.Leader:
                    await ctx.author.remove_roles(role)
                    await ctx.respond(f'You have left the force {name}')
                else:
                    await ctx.respond(
                        f'you are not in the force {name} and or are the leader and can not leave the force.'
                    )
            else:
                await ctx.respond(f'no force found with the name: {force}')
        else:
            await ctx.respond(f'no forces found with the name: {force}')

    @memberCommandGroup.command(guild_ids=[*guildids],
                                description="add a member to a force")
    async def add(self, ctx, force: Option(str,
                                           "the force to add the member to",
                                           required=True),
                  member: Option(str, "the name of the member", required=True),
                  role: Option(
                      str,
                      "the role of the member, Ex: officer, junior etc",
                      required=True), doc: Option(str,
                                                  'A link for the character',
                                                  required=True)):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            members = dbForce.Members
            dict = {"Name": member, "Role": role, "Doc": doc}
            if members != None:
                members.append(dict)
            else:
                members = [dict]
            dbForce.save()
            await ctx.respond(
                f"{role} {member} has been added to {dbForce.Name}")
        else:
            await ctx.respond(f"no force found with the name {force}",
                              ephemeral=True)

    @memberCommandGroup.command(guild_ids=[*guildids],
                                description="list the members in a force")
    async def list(self, ctx, force: Option(str,
                                            "the force to add the member to",
                                            required=True),
                   public: Option(bool,
                                  "Will show the result to only you if false",
                                  default=True)):
        dbForce = Force.searchDatabase(force)
        if dbForce != None:
            embed = dbForce.createMemberEmbed()
            await ctx.respond(embed=embed, ephemeral=not public)
        else:
            await ctx.respond(f"no force found with the name {force}",
                              ephemeral=True)

    @memberCommandGroup.command(guild_ids=[*guildids],
                                description="remove a member from a force")
    async def remove(
        self, ctx, force: Option(str,
                                 "the force to remove the memebr from.",
                                 required=True),
        member: Option(str,
                       "the member to remove from the force",
                       required=True),
        public: Option(bool,
                       "whether or not to make the response public",
                       required=False)):
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
            await ctx.respond(f"no force found with the name {force}",
                              ephemeral=True)
        if not memberFound:
            await ctx.respond(f"{member} is not a member of {force}",
                              ephemeral=True)

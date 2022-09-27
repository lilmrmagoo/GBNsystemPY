import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ui import InputText, Modal, View, Button
from replit import db
from shared import adminRoles, validation, guildIds

guildids = guildIds


def totalStats(dict):
    totaled = []
    for i in range(len(dict["Stats"])):
        totaled[i] = dict["BaseStats"][i] + dict["StatUps"][i]
    return totaled

def createPageView(dict):
    view = PageView(timeout=300.0,disable_on_timeout=True)
    if "Stats" in dict.keys():
        view.add_item(FormNavButton(form=dict,label="Stats",page="stats"))
    view.add_item(FormNavButton(form=dict,label="Info",page="info"))
    return view
def createStatsEmbed(dict, owner):
    name = dict['Name']
    inlink = dict['Link']
    inimage = dict['Image']
    link = None
    image = None
    if validation.validGoogleDoc(inlink) or validation.validDiscordLink(inlink):
        link = inlink
    else:
        link = 'https://discord.com/channels/479493485037355022/591348299752013837/917927502872215552'
    if inimage.startswith('http'):
        image = inimage
    else:
        image = 'https://cdn.discordapp.com/avatars/826265731930128394/ce7d79e6332e54a9a394b42cb182ddf7.png?size=4096'
    embed = discord.Embed(title=f"{name}'s Stats", url=link, color=0x2ca098)
    embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
    embed.set_thumbnail(url=image)
    for i in dict["Stats"]:
        index = dict["Stats"].index(i)
        statValue = dict["BaseStats"][index]
        embed.add_field(name=i, value=statValue, inline=False)
    return embed


def createEmbed(dict, owner):
    desc = dict['Desc']
    inlink = dict['Link']
    inimage = dict['Image']
    id = "Id: " + str(dict["ID"])
    link = None
    image = None
    if validation.validGoogleDoc(inlink) or validation.validDiscordLink(
            inlink):
        link = inlink
    else:
        link = 'https://discord.com/channels/479493485037355022/591348299752013837/917927502872215552'
    if inimage.startswith('http'):
        image = inimage
    else:
        image = 'https://cdn.discordapp.com/avatars/826265731930128394/ce7d79e6332e54a9a394b42cb182ddf7.png?size=4096'
    embed = discord.Embed(title=dict['Name'],
                          url=link,
                          description=desc,
                          color=0x2ca098)
    embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
    embed.set_thumbnail(url=image)
    embed.set_footer(text=id)
    embed = validation.addFieldsToEmbed(dict, embed)
    return embed

# coppied from the pycord examples
class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.interaction = None
    # When the confirm button is pressed, set the inner value
    # to `True` and stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.interaction = await interaction.response.send_message("Confirming...")
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.interaction = await interaction.response.send_message("Canceling...",ephemeral=True)
        self.value = False
        self.stop()

class PageView(View):
    def __init__(self, timeout=300,disable_on_timeout=True):
        super().__init__(timeout=timeout)
        self.disable_on_timeout=disable_on_timeout
    async def on_timeout(self):
        self.disable_all_items()
        self.clear_items()
        await self.interaction.edit_original_message(view=None)
    def set_interaction(self, interaction):
        self.interaction = interaction
class FormNavButton(Button):
    def __init__(self,page=None,form=None,label=None):
        super().__init__(label=label,style=discord.ButtonStyle.primary)
        self.page = page
        self.form = form
    async def callback(self, interaction: discord.Interaction):
        form = self.form
        user = interaction.user
        response = interaction.response
        if self.page.casefold() == "stats":
            await response.edit_message(embed=createStatsEmbed(form,user))
        if self.page.casefold() == "info":
            await response.edit_message(embed=createEmbed(form,user))

class OpenModalButton(Button):
    def __init__(self,modal=None,label=None):
        super().__init__(label=label,style=discord.ButtonStyle.primary)
        self.modal = modal
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_modal(self.modal)
class StatsModal(Modal):
    def __init__(self,template=None,mode=0,form=None,owner=None,*args,**kwargs) -> None:
        super().__init__(*args, **kwargs)
        names = ["Stat 1", "Stat 2", "Stat 3", "Stat 4", "Stat 5"]
        if template == "Basic(Gunpla)":
            names = ["Mobility", "Armour", "Melee Atk", "Ranged Atk"]
        elif template == ("Basic(Character)"):
            names = ["Dexterity","Strength","Inteligence","Charisma","Constitution"]
        self.mode = mode
        self.form = form
        self.owner = owner
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        validform = False
        if mode == 1:
            for i in userForms:
                if i["Name"].casefold().startswith(form.casefold()):
                    i["Stats"] = names
                    validform=True
        if mode == 1 and not validform:
            return None
        if mode == 0:
            for i in range(len(names)):
                try:
                    self.add_item(InputText(label=names[i],
                                  placeholder="Put the name of the stat",
                                  style=discord.InputTextStyle.short,
                                  row=i,
                                  required=False))
                except:
                    break
        elif mode == 1:
            for i in range(len(names)):
                try:
                    self.add_item(
                        InputText(label=names[i],
                                  placeholder="Put the value of the stat",
                                  style=discord.InputTextStyle.short,
                                  row=i,
                                  required=False,))
                except:
                    break

    async def callback(self, interaction: discord.Interaction):
        dataBaseKey = str(self.owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        if self.mode == 0:
            stats = []
            for i in self.children:
                if i.value != None and i.value != "":
                    stats.append(i.value)
            for i in userForms:
                if i["Name"].casefold().startswith(self.form.casefold()):
                    i["Stats"] = stats
                    i["BaseStats"] = [0] * len(i["Stats"])
                    embed = createStatsEmbed(i, self.owner)
                    view = createPageView(i)
                    reaction= await interaction.response.send_message(embed=embed,ephemeral=True,view=view)
                    view.set_interaction(reaction)
        elif self.mode == 1:
            stats = []
            for i in self.children:
                if i.value != None:
                    stats.append(i.value)
            for i in userForms:
                if i["Name"].casefold().startswith(self.form.casefold()):
                    i["BaseStats"] = stats
                    embed = createStatsEmbed(i, self.owner)
                    view = createPageView(i)
                    reaction= await interaction.response.send_message(embed=embed,ephemeral=True,view=view)
                    view.set_interaction(reaction)


class FormModal(Modal):
    def __init__(self,type=None,oldValues=None,owner=None,edit=False,*args,**kwargs) -> None:
        self.owner = owner
        self.edit = edit
        self.type = type
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
                          row=1))
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
            super().__init__(*args, **kwargs)
            self.add_item(
                InputText(label="Name",
                          placeholder="Put the name here",
                          style=discord.InputTextStyle.short,
                          row=0,
                          value=oldValues['Name']))
            self.add_item(
                InputText(label="Description",
                          placeholder="describe the form here",
                          style=discord.InputTextStyle.long,
                          row=1,
                          value=oldValues['Desc']))
            self.add_item(
                InputText(label="Image",
                          placeholder="put a link to an image here",
                          style=discord.InputTextStyle.short,
                          row=2,
                          required=False,
                          value=oldValues['Image']))
            self.add_item(
                InputText(
                    label="Document",
                    placeholder=
                    "put a link to a google doc or discord message link here",
                    style=discord.InputTextStyle.short,
                    row=3,
                    value=oldValues['Link']))
            self.oldName = oldValues['Name']

    async def callback(self, interaction: discord.Interaction):
        googledoc = self.children[3].value
        desc = self.children[1].value
        image = self.children[2].value
        name = self.children[0].value
        owner = self.owner
        del db["IDs"] 
        if not validation.doesKeyExist("IDs"):
            db["IDs"]= {}
            IDs = db["IDs"]
            IDs["LastFormID"] = 0
        else: 
            IDs = db["IDs"]
        id = IDs["LastFormID"] + 1
        if not self.edit:
            IDs["LastFormID"] = id
        if owner == None:
            owner = interaction.user
        formtype = self.type
        dataBaseKey = str(owner.id) + "'s forms"
        dict = {
            "Name": name,
            "Link": googledoc,
            "Form Type": formtype,
            "Desc": desc,
            "Image": image
        }
        userForms = db.get(dataBaseKey)
        if self.edit:
            if "ID" not in dict.keys():
                IDs["LastFormID"] = id
                dict["ID"] = id
            for i in userForms:
                if i['Name'] == self.oldName:
                    index = userForms.index(i)
                    userForms[index] = dict
                    embed = createEmbed(dict, owner)
                    await interaction.response.send_message(
                        f"{owner}'s {formtype} has been edited!",
                        embed=embed,
                        ephemeral=True)
        else:
            dict["ID"] = id
            if validation.doesKeyExist(dataBaseKey):
                userForms.append(dict)
                db[dataBaseKey] = userForms
            else:
                db[dataBaseKey] = [dict]
            embed = createEmbed(dict, owner)
            if formtype=="Other":
                modal = StatsModal(template="Custom",mode=0,form=dict["Name"],owner=owner,title="Name Stats")
            else:
                modal = StatsModal(template=f"Basic({formtype})",mode=1,form=dict["Name"],owner=owner,title="Assign Stats")
            view = View(timeout=300)
            view.add_item(OpenModalButton(modal=modal,label="Create Stats?"))
            await interaction.response.send_message(f"{owner}'s {formtype} has been created!",embed=embed,view=view,ephemeral=True)


class FormCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    form = SlashCommandGroup('form', "commands to get edit or create forms")
    stats = form.create_subgroup('stats', 'commands to add stats to a form')


    @discord.commands.user_command(name="list forms",guild_ids=[*guildids])
    async def list_forms(self, ctx: discord.ApplicationContext,member: discord.Member):
        owner = member
        dataBaseKey = str(owner.id) + "'s forms"
        if validation.doesKeyExist(dataBaseKey):
            userForms = db.get(dataBaseKey)
            embed = discord.Embed(title=f"{owner}'s forms", color=0x2ca098)
            gunplas = ' '
            characters = ' '
            others = ' '
            for i in userForms:
                name = i['Name']
                if i['Form Type'] == 'Gunpla':
                    gunplas = f'{gunplas}\n{name}'
                elif i['Form Type'] == 'Character':
                    characters = f'{characters}\n{name}'
                elif i['Form Type'] == 'Other':
                    others = f'{others}\n{name}'
            
            if gunplas != ' ': embed.add_field(name='Gunpla Forms', value=gunplas)
            if characters != ' ': embed.add_field(name='Character Forms', value=characters)
            if others != ' ': embed.add_field(name='Other Forms',value=others,)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond('That user does not have any forms')
    @discord.commands.user_command(name="Create a Gunpla for user",guild_ids=[*guildids])
    async def create_gunpla(self, ctx: discord.ApplicationContext,member: discord.Member):
        if ctx.author == member or validation.userHasRole(
                ctx.author, adminRoles):
            modal = FormModal(title=f"Create a Gunpla form for {member}",
                              type="Gunpla",
                              owner=member)
            await ctx.send_modal(modal)
        else:
            await ctx.respond(
                "You do not have permision to create a form for someone else.",
                ephemeral=True)

    @discord.commands.user_command(name="Create a Character for user",guild_ids=[*guildids])
    async def create_character(self, ctx: discord.ApplicationContext,member: discord.Member):
        if ctx.author == member or validation.userHasRole(
                ctx.author, adminRoles):
            modal = FormModal(title=f"Create a Character form for {member}",
                              type="Character",
                              owner=member)
            await ctx.send_modal(modal)
        else:
            await ctx.respond(
                "You do not have permision to create a form for someone else.",
                ephemeral=True)

    @discord.commands.user_command(name="Create an Other form for user",guild_ids=[*guildids])
    async def create_other(self, ctx: discord.ApplicationContext,member: discord.Member):
        if ctx.author == member or validation.userHasRole(
                ctx.author, adminRoles):
            modal = FormModal(title=f"Create a Other form for {member}",
                              type="Other",
                              owner=member)
            await ctx.send_modal(modal)
        else:
            await ctx.respond(
                "You do not have permision to create a form for someone else.",
                ephemeral=True)

    @form.command(guild_ids=[*guildids],description='Create a character or gunpla form that people can access')
    async def create(self, ctx, formtype: Option(str, "type of form",choices=["Gunpla", "Character", "Other"],required=True)):
        print('command createform activated')
        modal = FormModal(title=f"Create a {formtype} Form", type=formtype)
        await ctx.send_modal(modal)

    @form.command(guild_ids=[*guildids],description="delete a gunpla or character")
    async def delete(self, ctx, 
                     form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'',required=True), 
                     by: Option(str,'the selector used to delete the form', choices=['Name', 'Id'], required=False, default='Name'),
                     owner: Option(discord.Member, 'the owner of the form. Requires perms to use', required=False, default=None)
    ):
        if owner == None:
            owner = ctx.author
        elif validation.userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to delete someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        validform=False
        if by == 'Id':
            for i in userForms:
                if userForms.index(i) == form:
                    validform=True
                    name = i["Name"]
                    formtype = i["Form Type"]
                    view = Confirm()
                    ctx.respond(f"Are you sure you want to delete the form {name}?", view=view, ephemeral=True,delete_after=240.0)
                    await view.wait()
                    interaction = view.interaction
                    if view.value == None:
                        await interaction.edit_original_message(content=f'timed out')
                        break
                    elif view.value:
                        userForms.remove(i)
                        await interaction.edit_original_message(content=f"{formtype} Form: {form} deleted by {by}",view=None)
                        break
                    else:
                        await interaction.edit_original_message(content=f'Canceled')
        elif by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    validform=True
                    name = i["Name"]
                    formtype = i["Form Type"]
                    view = Confirm()
                    await ctx.send_response(f"Are you sure you want to delete the form {name}?", view=view, ephemeral=True, delete_after=240.0)
                    await view.wait()
                    interaction = view.interaction
                    if view.value == None:
                        await interaction.edit_original_message(content=f'Interaction timed out')
                        break
                    elif view.value:
                        userForms.remove(i)
                        await interaction.edit_original_message(content=f"{formtype} Form: {form} deleted by {by}",view=None)
                        break
                    else:
                        await interaction.edit_original_message(content=f'Interaction Canceled')
        if not validform:
            await ctx.respond(f'form {form} not found',ephemeral=True)
    @form.command(guild_ids=[*guildids],description="get someone's character or gunpla")
    async def get(self, ctx, 
            form: Option(str, 'the form you want to get. ex: \'My gundam\' or \'my character\'',required=True),
            owner: Option(discord.Member,'the owner of the form. deafult is command activator',required=False,default=None),
            public: Option(bool,"makes the message only visible to you if false, True by default",required=False,default=True),
            by: Option(str, 'the selector used to get the form, default is by name',choices=['Name', 'Id'],required=False,default='Name')
        ):
        print('command get activated')
        if owner == None:
            owner = ctx.author
        dataBaseKey = str(owner.id) + "'s forms"
        if validation.doesKeyExist(dataBaseKey):
            userForms = db.get(dataBaseKey)
            if by == 'Id':
                for i in userForms:
                    if userForms.index(i) == form:
                        view = createPageView(i)
                        embed = createEmbed(i,owner)
                        interaction = await ctx.respond(embed=embed,view=view, ephemeral=not public)
                        view.set_interaction(interaction)
                        break
                    elif userForms.index(i) + 1 == len(userForms):
                        await ctx.respond(
                            f'no form found with selector: {by} and value: {form} from user: {owner}',
                            ephemeral=True)
                        break
            elif by == 'Name':
                for i in userForms:
                    if i['Name'].casefold().startswith(form.casefold()):
                        view = createPageView(i)
                        embed = createEmbed(i,owner)
                        interaction = await ctx.respond(embed=embed,view=view, ephemeral=not public)
                        view.set_interaction(interaction)
                        break
                    elif userForms.index(i) + 1 == len(userForms):
                        await ctx.respond(
                            f'no form found with selector: {by} and value: {form} from user: {owner}',
                            ephemeral=True)
                        break
            else:
                await ctx.respond(
                    f'no form found with selector:{by} and value:{form}',
                    ephemeral=True)
        else:
            await ctx.respond(f'{owner} has no forms', ephemeral=True)

    @form.command(guild_ids=[*guildids], description="edit the data of a form")
    async def oldedit(
        self, ctx, form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'',required=True),
        inputfield: Option(str,'the field you want to edit',choices=["Name", "Link", "Desc", "Image", "Type"],required=True),
        inputdata: Option(str,'the data you want to set the input field to',required=True),
        by: Option(str,'the selector used to get the form',choices=['Name', 'Id'],required=False,default='Name'),
        owner: Option(discord.Member,'the owner of the form. deafult is command activator',required=False,default=None)):
        if owner == None:
            owner = ctx.author
        elif validation.userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to edit someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        if by == 'Id':
            for i in userForms:
                if userForms.index(i) == form:
                    index = userForms.index(i)
                    userForms[index][inputfield] = inputdata
                    await ctx.respond(
                        f'{inputfield} changed to {inputdata} on id: {userForms.index(i)}',
                        ephemeral=True)
                    break
        elif by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    index = userForms.index(i)
                    userForms[index][inputfield] = inputdata
                    await ctx.respond(
                        f'{inputfield} changed to {inputdata} on {i["Name"]}',
                        ephemeral=True)
                    break

    @form.command(guild_ids=[*guildids], description="edit the data of a form")
    async def edit(self, ctx, form: Option(str,"the form to edit",required=True)):
        dataBaseKey = str(ctx.author.id) + "'s forms"
        userForms = db[dataBaseKey]
        validform=False
        for i in userForms:
            if i['Name'].casefold().startswith(form.casefold()):
                validform=True
                modal = FormModal(title=f"Edit your {i['Name']} Form",
                                  edit=True,
                                  oldValues=i,
                                  type=i['Form Type'])
                await ctx.send_modal(modal)
        if not validform:
            await ctx.respond(f"no form found with name {form}", ephemeral=True)
    @form.command(guild_ids=[*guildids])
    async def addfield(self, ctx, 
        fieldname: Option(str,'the name of the field',required=True),
        fielddata: Option(str, 'the data for the field', required=True),
        form: Option(str, "the form to add the field to", required=True),
        inline: Option(bool,"will make the field apear to the left of the previous one",required=True),
        owner: Option(discord.Member,"the owner of the form requires perms",required=False,default=None), 
        by: Option(str,"what to search by",choices=["Name", 'Id'],required=False,default='Name')):
        if owner == None:
            owner = ctx.author
        elif validation.userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to edit someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        if inline == True:
            fieldname = fieldname + '#INLINE'
        if by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    name = fieldname.strip('#INLINE')
                    index = userForms.index(i)
                    userForms[index][fieldname] = fielddata
                    await ctx.respond(
                        f'{fielddata} added to {name} in {i["Name"]}',
                        ephemeral=True)
                    break

    @form.command(guild_ids=[*guildids])
    async def removefield(self, ctx, fieldname: Option(str,'the name of the field',required=True),
                          form: Option(str,"the form to add the field to",required=True),
                          owner: Option(discord.Member,"the owner of the form requires perms",required=False,default=None)):
        if owner == None:
            owner = ctx.author
        elif validation.userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to edit someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        for i in userForms:
            if i['Name'].casefold().startswith(form.casefold()):
                index = userForms.index(i)
                inlineField = fieldname + '#INLINE'
                if userForms[index][fieldname] in userForms[index]:
                    del userForms[index][fieldname]
                    await ctx.respond(f"field {fieldname} removed from {form}")
                elif userForms[index][inlineField] in userForms[index]:
                    del userForms[index][inlineField]
                    await ctx.respond(f"field {fieldname} removed from {form}")
                else:
                    await ctx.respon * (
                        f'no field found with name {fieldname}')

    @form.command(guild_ids=[*guildids],description="find a character or gunpla")
    async def search(self, ctx, 
                     form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'',required=True), 
                     public: Option(bool,"makes the message only visible to you if false, True by default",required=False,default=True)
    ):
        print(f'searching in guild {ctx.guild}...')
        searchComplete = False
        keys = db.keys()
        for j in keys:
            if j.endswith('forms'):
                userForms = db.get(j)
                guild = ctx.guild
                memberid = j[0:-8]
                try:
                    owner = await guild.fetch_member(memberid)
                except discord.errors.NotFound:
                    continue
                for i in userForms:
                    if i['Name'].casefold().startswith(form.casefold()):
                        searchComplete = True
                        view = createPageView(i)
                        interaction= await ctx.respond(embed=createEmbed(i, owner),view=view,ephemeral=not public)
                        view.interaction = interaction
                        break
                if searchComplete:
                    break
        if not searchComplete:
            await ctx.respond(f'no form found with name {form}',
                              ephemeral=not public)

    @form.command(guild_ids=[*guildids],description="get a list of a users forms")
    async def list(self, ctx, owner: Option(discord.Member, "the person who's forms you wish to get",required=False,default=None)):
        if owner == None:
            owner = ctx.author
        dataBaseKey = str(owner.id) + "'s forms"
        if validation.doesKeyExist(dataBaseKey):
            userForms = db.get(dataBaseKey)
            embed = discord.Embed(title=f"{owner}'s forms", color=0x2ca098)
            gunplas = ''
            characters = ''
            others = ''
            for i in userForms:
                name = i['Name']
                if i['Form Type'] == 'Gunpla':
                    gunplas = f'{gunplas}\n{name}'
                elif i['Form Type'] == 'Character':
                    characters = f'{characters}\n{name}'
                elif i['Form Type'] == 'Other':
                    others = f'{others}\n{name}'
            if gunplas != '': embed.add_field(name='Gunpla Forms', value=gunplas)
            if characters != '': embed.add_field(name='Character Forms', value=characters)
            if others != '': embed.add_field(name='Other Forms',value=others,)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond('That user does not have any forms')

    @stats.command(guild_ids=[*guildids],description="create a stats page for a form", name="create")
    async def create_stats(self, ctx, 
                           form: Option(str,"the form to which tha stats will be added"),
                           preset: Option(str,"presets for stat templates",choices=["Basic(Gunpla)", "Basic(Character)","Custom"])
    ):
        owner = ctx.author
        if preset == "Custom":
            modal = StatsModal(title="Set the base stats",template=preset,mode=0,form=form,owner=owner)
        else:
            modal = StatsModal(title="Name your stats",template=preset,mode=1,form=form,owner=owner)

        if not modal == None:
            await ctx.send_modal(modal)
        else:
            await ctx.respond(f"No form found with the name{form}", ephemeral=True)
    
    @stats.command(guild_ids=[*guildids],description="remove a stats page from a form", name="remove")
    async def remove_stats(self, ctx, form: Option(str,"the form to which tha stats will be added"),
    ):
        owner = ctx.author
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        validform=False
        for i in userForms:
            if i['Name'].casefold().startswith(form.casefold()):
                validform=True
                keys = i.keys()
                if "Stats" in keys:
                    del i["Stats"]
                if "BaseStats" in keys:
                    del i["BaseStats"]
                await ctx.respond("stats removed", ephemeral=True)
        if not validform:
            await ctx.respond("not a valid form")
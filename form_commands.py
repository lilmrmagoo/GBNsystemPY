import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from replit import db
from shared import adminRoles, validation, guildIds
guildids = guildIds

class FormCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    form = SlashCommandGroup('form', "commands to get edit or create forms")
  
    
    @form.command(guild_ids=[*guildids], description='Create a character or gunpla form that people can access')
    async def create(self, ctx, 
        googledoc: Option(str,"the form link, or discord message link",required=True),
        formtype: Option(str,"type of form",choices=["Gunpla", "Character", "Other"],required=True),
        name: Option(str,"Name for character or gunpla",required=True),
        owner: Option(discord.Member,"The owner of the form",required=False)
    ):
        print('command createform activated')
        if validation.validGoogleDoc(googledoc) or validation.validDiscordLink(googledoc):
            if owner == None:
                owner = ctx.author
            dataBaseKey = str(owner.id) + "'s forms"
            if validation.doesKeyExist(dataBaseKey):
                userForms = db.get(dataBaseKey)
                userForms.append({
                    "Name": name,
                    "Link": googledoc,
                    "Form Type": formtype,
                    "Desc":'',
                    "Image":''
                })
                db[dataBaseKey] = userForms
            else:
                newDict = {"Name": name, "Link": googledoc, "Form Type": formtype, "Desc":'','Image':''}
                db[dataBaseKey] = [newDict]
            await ctx.respond(f"{owner}'s {formtype} has been created!")
            print(dataBaseKey)
            print(db[dataBaseKey])
    
        else:
            await ctx.respond('non valid link provided')
            print(owner)
    
    
    @form.command(guild_ids=[*guildids], description="delete a gunpla or character")
    async def delete(
        self, ctx, 
        form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'',required=True),
        by: Option(str,'the selector used to delete the form',choices=['Name', 'Id'],required=False,default='Name'),
        owner: Option(discord.Member,'the owner of the form. Requires perms to use',required=False,default=None)):
        if owner == None:
            owner = ctx.author
        elif validation.userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to delete someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        if by == 'Id':
            for i in userForms:
                if userForms.index(i) == form:
                    del userForms[form]
                    await ctx.respond(f'{type}#{form} deleted by {by}')
                    break
        elif by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    userForms.remove(i)
                    await ctx.respond(f'{i["Form Type"]}: {form} deleted by {by}')
                    break
    
    
    @form.command(guild_ids=[*guildids], description="get someone's character or gunpla")
    async def get(
        self, ctx, 
        form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'' ,required=True),
        owner: Option(discord.Member,'the owner of the form. deafult is command activator',required=False,default=None),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=True),
        by: Option(str,'the selector used to get the form, default is by name',choices=['Name', 'Id'],required=False, default='Name')
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
                        desc = i['Desc']
                        embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
                        embed.set_thumbnail(url=i['Image'])
                        embed.set_footer(text=f"id: {userForms.index(i)}")
                        embed = validation.addFieldsToEmbed(i, embed)
                        await ctx.respond(embed=embed,ephemeral=not public)
                        break
                    elif userForms.index(i)+1 == len(userForms):
                        await ctx.respond(f'no form found with selector: {by} and value: {form} from user: {owner}', ephemeral=True)
                        break
            elif by == 'Name':
                for i in userForms:
                    if i['Name'].casefold().startswith(form.casefold()):
                        desc = i['Desc']
                        embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
                        embed.set_thumbnail(url=i['Image'])
                        embed = validation.addFieldsToEmbed(i, embed)
                        await ctx.respond(embed=embed,ephemeral=not public)
                        break
                    elif userForms.index(i)+1 == len(userForms):
                        await ctx.respond(f'no form found with selector: {by} and value: {form} from user: {owner}', ephemeral=True)
                        break
            else: await ctx.respond(f'no form found with selector:{by} and value:{form}', ephemeral=True)
        else: await ctx.respond(f'{owner} has no forms', ephemeral=True)
    
    @form.command(guild_ids=[*guildids], description="edit the data of a form")
    async def edit(
        self, ctx, 
        form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'' ,required=True),        
        inputfield: Option(str,'the field you want to edit', choices=["Name","Link","Desc","Image","Type"],required=True),
        inputdata: Option(str,'the data you want to set the input field to', required=True),
        by: Option(str,'the selector used to get the form',choices=['Name', 'Id'],required=False,default='Name'),
        owner: Option(discord.Member,'the owner of the form. deafult is command activator',required=False,default=None)
    ):
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
                    index= userForms.index(i)
                    userForms[index][inputfield] = inputdata
                    await ctx.respond(f'{inputfield} changed to {inputdata} on id: {userForms.index(i)}',ephemeral=True)
                    break
        elif by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    index= userForms.index(i)
                    userForms[index][inputfield] = inputdata
                    await ctx.respond(f'{inputfield} changed to {inputdata} on {i["Name"]}',ephemeral=True)
                    break
    
    @form.command(guild_ids=[*guildids])
    async def addfield(self, ctx,
        fieldname: Option(str, 'the name of the field',required=True),
        fielddata: Option(str, 'the data for the field',required=True),
        form: Option(str, "the form to add the field to",required=True),
        inline: Option(bool, "will make the field apear to the left of the previous one",required=True),
        owner: Option(discord.Member, "the owner of the form requires perms", required=False,default=None),
        by: Option(str,"what to search by", choices=["Name", 'Id'], required=False, default='Name')
    ):
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
                    index=userForms.index(i)
                    userForms[index][fieldname] = fielddata
                    await ctx.respond(f'{fielddata} added to {name} in {i["Name"]}',ephemeral=True)
                    break
        elif by == 'Id':
            for i in userForms:
                if userForms.index(i) == form:
                    index=userForms.index(i)
                    userForms[index][fieldname] = fielddata
                    await ctx.respond(f'{fielddata} added to {fieldname} in {i["Name"]}',ephemeral=True)
                    break
    
    @form.command(guild_ids=[*guildids])
    async def removefield(self, ctx,
        fieldname: Option(str, 'the name of the field',required=True),
        form: Option(str, "the form to add the field to",required=True),
        owner: Option(discord.Member, "the owner of the form requires perms", required=False,default=None)
    ):
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
                index=userForms.index(i)
                inlineField = fieldname + '#INLINE'
                if userForms[index][fieldname] in userForms[index]: 
                    del userForms[index][fieldname]
                    await ctx.respond(f"field {fieldname} removed from {form}")
                elif userForms[index][inlineField] in userForms[index]:
                    del userForms[index][inlineField]
                    await ctx.respond(f"field {fieldname} removed from {form}")
                else:
                    await ctx.respon*(f'no field found with name {fieldname}')
    @form.command(guild_ids=[*guildids], description="find a character or gunpla")
    async def search(
        self, ctx, 
        form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'' ,required=True),
        public: Option(bool, "makes the message only visible to you if false, True by default",required=False, default=True)
    ):
        print(f'searching in guild {ctx.guild}...')
        
        searchComplete = False
        keys = db.keys()
        for j in keys:
            if j.endswith('forms'):
                userForms = db.get(j)
                guild = ctx.guild
                memberid = j[0:-8]
                owner = await guild.fetch_member(memberid)
                for i in userForms:
                    if i['Name'].casefold().startswith(form.casefold()):
                        searchComplete = True                        
                        desc = i['Desc']
                        embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
                        embed.set_thumbnail(url=i['Image'])
                        embed = validation.addFieldsToEmbed(i, embed)
                        await ctx.respond(embed=embed,ephemeral=not public)
                        break
                if searchComplete:
                    break
        if not searchComplete:
            await ctx.respond(f'no form found with name {form}', ephemeral=not public)
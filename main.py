impleimport keepalive
import discord
from discord.commands import Option, permissions, SlashCommandGroup, slash_command
from discord.ext import commands
import os
from replit import db
from force_commands import ForceCommands
keepalive.keep_alive()
bot = discord.Bot()
token = os.environ['TOKEN']
adminRoles = ['helper', 'Moderators', 'Owner']
guildids= [479493485037355022,472944754397806619]




def addFieldsToEmbed(dict, embed):
    for i in dict:
        if list(dict.keys()).index(i) > 4: 
            embed.add_field(name=i, value=dict[i], inline=True)
    return embed
# pretty useless now i think unsure don't want to break
def findGapInIds(dict, type):
    id = f'{type}#1'
    iterable = 1
    for i in dict:
        print(i)
        if i.startswith(type):
            if id in dict.keys():
                id = f'{type}#{iterable+1}'
                print("id equals : " + id)
                iterable += 1
                continue
    return int(id[id.find('#') + 1:])


def countKeysWith(dict, type):
    dictKeys = dict.keys()
    count = 0
    for i in dictKeys:
        if i.startswith(type):
            count += 1
    return count


def validGoogleDoc(input):
    link = "https://docs.google.com/"
    if (input.startswith(link)):
        return True
    else:
        return False

def validDiscordLink(input):
    link = "https://discord.com/"
    if (input.startswith(link)):
        return True
    else:
        return False

def doesKeyExist(key):
    if db.prefix(key): return True
    else: return False


def userHasRole(member, role):
    membersRoles = member.roles
    if isinstance(role, str):
        if (membersRoles.count(role) > 0):
            return True
        else:
            return False
    elif isinstance(role, list):
        for i in role:
            if (membersRoles.count(i) > 0):
                return True
        return False


#@bot.on_ready()
#async def on_ready(self):
#print(f'system online logged in as {self}')
class FormAndDev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    dev = SlashCommandGroup("dev", "Commands for bot development. DO NOT USE unless you know what you are doing.",
        permissions=[
                   permissions.CommandPermission("Owner", 1, True
                )
            ])
    form = SlashCommandGroup('form', "commands to get edit or create forms")
    #force = SlashCommandGroup('force', 'commands to edit or create forces.', 
#        permissions=[
 #               permissions.CommandPermission(
 #                   "Owner", 1, True
   #             )
  #          ])
    
    
    
    @form.command(guild_ids=[*guildids], description='Create a character or gunpla form that people can access')
    async def create(self, ctx, 
        googledoc: Option(str,"the form link, or discord message link",required=True),
        formtype: Option(str,"type of form",choices=["Gunpla", "Character", "Other"],required=True),
        name: Option(str,"Name for character or gunpla",required=True),
        owner: Option(discord.Member,"The owner of the form",required=False)
    ):
        print('command createform activated')
        if validGoogleDoc(googledoc) or validDiscordLink(googledoc):
            if owner == None:
                owner = ctx.author
            dataBaseKey = str(owner.id) + "'s forms"
            if doesKeyExist(dataBaseKey):
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
    
    
    @form.command(guild_ids=[*guildids],description="delete a gunpla or character")
    async def delete(
        self, ctx, 
        form: Option(str,'the form you want to get. ex: \'My gundam\' or \'my character\'',required=True),
        by: Option(str,'the selector used to delete the form',choices=['Name', 'Id'],required=False,default='Name'),
        owner: Option(discord.Member,'the owner of the form. Requires perms to use',required=False,default=None)):
        if owner == None:
            owner = ctx.author
        elif userHasRole(ctx.author, adminRoles) != True:
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
        if doesKeyExist(dataBaseKey):
            userForms = db.get(dataBaseKey)
            if by == 'Id':
                for i in userForms:
                    if userForms.index(i) == form:
                        desc = i['Desc']
                        embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
                        embed.set_thumbnail(url=i['Image'])
                        embed.set_footer(text=f"id: {userForms.index(i)}")
                        embed = addFieldsToEmbed(i, embed)
                        await ctx.respond(embed=embed,ephemeral=not public)
                        break
                    else:
                        await ctx.respond(f'no form found with id:{form}')
            elif by == 'Name':
                for i in userForms:
                    if i['Name'].casefold().startswith(form.casefold()):
                        desc = i['Desc']
                        embed=discord.Embed(title=i['Name'], url=i['Link'], description=desc, color=0x2ca098)
                        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
                        embed.set_thumbnail(url=i['Image'])
                        embed.set_footer(text=f"id: {userForms.index(i)}")
                        embed = addFieldsToEmbed(i, embed)
                        await ctx.respond(embed=embed,ephemeral=not public)
                        break
                    elif userForms.index(i)+1 == len(userForms):
                        await ctx.respond(f'no form found with selector: {by} and value: {form} from user: {owner}', ephemeral=True)
                        break
            else: await ctx.respond(f'no form found with selector:{by} and value:{form}', ephemeral=True)
        else: await ctx.respond(f'{owner} has no forms', ephemeral=True)
    
    @form.command(guild_ids=[*guildids],description="edit the data of a form")
    async def edit(
        ctx, 
        form: Option(str,'the form you want to get. ex: \'1\' or \'og gundam\'',required=True),
        inputfield: Option(str,'the field you want to edit', choices=["Name","Link","Desc","Image","Type"],required=True),
        inputdata: Option(str,'the data you want to set the input field to', required=True),
        by: Option(str,'the selector used to get the form',choices=['Name', 'Id'],required=False,default='Name'),
        owner: Option(discord.Member,'the owner of the form. deafult is command activator',required=False,default=None)
    ):
        if owner == None:
            owner = ctx.author
        elif userHasRole(ctx.author, adminRoles) != True:
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
        owner: Option(discord.Member, "the owner of the form requires perms", required=False,default=None),
        by: Option(str,"what to search by", choices=["Name", 'Id'], required=False, default='Name')
    ):
        if owner == None:
            owner = ctx.author
        elif userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to edit someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        if by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    index=userForms.index(i)
                    userForms[index][fieldname] = fielddata
                    await ctx.respond(f'{fielddata} added to {fieldname} in {i["Name"]}',ephemeral=True)
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
        owner: Option(discord.Member, "the owner of the form requires perms", required=False,default=None),
        by: Option(str,"what to search by", choices=["Name", 'Id'], required=False, default='Name')
    ):
        if owner == None:
            owner = ctx.author
        elif userHasRole(ctx.author, adminRoles) != True:
            ctx.respond(
                "You do not have permission to edit someone else's forms.",
                ephemeral=True)
            return
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        if by == 'Name':
            for i in userForms:
                if i['Name'].casefold().startswith(form.casefold()):
                    index=userForms.index(i)
                    del userForms[index][fieldname]
                    await ctx.respond(f"field {fieldname} removed from {form}")
                    break
        elif by == 'Id':
            for i in userForms:
                if userForms.index(i) == form:
                    index=userForms.index(i)
                    del userForms[index][fieldname]
                    await ctx.respond(f"field {fieldname} removed from {form}")
                    break
    
    @dev.command(guild_ids=[*guildids])
    async def delkey(self, ctx, owner: Option(discord.Member,'the users forms to delete')):
        dataBaseKey = str(owner.id) + "'s forms"
        del db[dataBaseKey]
        await ctx.respond('key has been deleted', ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def getkey(self, ctx, owner: Option(discord.Member,'returns all a users values under their form key')):
        dataBaseKey = str(owner.id) + "'s forms"
        await ctx.respond(str(db[dataBaseKey]), ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def updatekey(self, ctx, owner: Option(discord.Member,'the users forms to update')):
        dataBaseKey = str(owner.id) + "'s forms"
        userForms = db[dataBaseKey]
        db[dataBaseKey] = list(userForms.values())
        await ctx.respond('key should be converted', ephemeral=True)
    @dev.command(guild_ids=[*guildids])
    async def allusers(self, ctx):
        users = db.keys()
        await ctx.respond(users, ephemeral=True)

#bot.add_application_command(form)
#bot.add_application_command(dev)
#bot.add_application_command(force)
bot.add_cog(FormAndDev(bot))
bot.add_cog(ForceCommands(bot))

bot.run(token)

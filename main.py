import keepalive
import discord
from discord.commands import Option, permissions
import os
from replit import db
keepalive.keep_alive()
bot = discord.Bot()
token = os.environ['TOKEN']
adminRoles = ['helper', 'Moderators', 'Owner']
guildids= [479493485037355022,472944754397806619]

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


@bot.slash_command(guild_ids=[*guildids])
async def createform(ctx, 
    googledoc: Option(str,"the form link",required=True),
    formtype: Option(str,"type of form",choices=["Gunpla", "Character", "Other"],required=True),
    name: Option(str,"Name for character or gunpla",required=True),
    owner: Option(discord.Member,"The owner of the form",required=False)
):
    print('command createform activated')
    if (validGoogleDoc(googledoc)):
        if owner == None:
            owner = ctx.author
        dataBaseKey = str(owner.id) + "'s forms"
        if doesKeyExist(dataBaseKey):
            userForms = db.get(dataBaseKey)
            gap = findGapInIds(userForms, formtype)
            userForms[f"{formtype}#{gap}"] = {
                "Name": name,
                "Link": googledoc,
                "Form Type": formtype,
                "Desc":'',
                "Image":''
            }
            db[dataBaseKey] = userForms
        else:
            newDict = {"Name": name, "Link": googledoc, "Form Type": formtype, "Desc":'','Image':''}
            db[dataBaseKey] = {f"{formtype}#1": newDict}
        await ctx.respond(f"{owner}'s {formtype} has been created!")
        print(dataBaseKey)
        print(db[dataBaseKey])

    else:
        await ctx.respond('non valid link provided')
        print(owner)


@bot.slash_command(guild_ids=[*guildids])
async def deleteform(
    ctx, 
    by: Option(str,'the selector used to delete the form',choices=['Name', 'Id'],required=True),
    form: Option(str,'the form you want to delete. ex: \'1\' or \'og gundam\'',required=True),
    type: Option(str,'the type of form being deleted',choices=["Gunpla", "Character", "Other"],required=True),
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
            if i.startswith(type):
                if i[i.find('#') + 1:] == form:
                    del userForms[i]
                    await ctx.respond(f'{type}#{form} deleted by {by}')
                    break
    elif by == 'Name':
        for i in userForms:
            if userForms[i]['Name'].casefold() == form.casefold():
                del userForms[i]
                await ctx.respond(f'{type}: {form} deleted by {by}')
                break


@bot.slash_command(guild_ids=[*guildids])
async def get(
    ctx, 
    by: Option(str,'the selector used to get the form',choices=['Name', 'Id'],required=True),
    form: Option(str,'the form you want to get. ex: \'1\' or \'og gundam\'',required=True),
    type: Option(str,'the type of form to get',choices=["Gunpla", "Character", "Other"],required=True),
    owner: Option(discord.Member,'the owner of the form. deafult is command activator',required=False,default=None)
):
    print('command get activated')
    if owner == None:
        owner = ctx.author  
    dataBaseKey = str(owner.id) + "'s forms"
    if doesKeyExist(dataBaseKey):
        userForms = db.get(dataBaseKey)
        if by == 'Id':
            for i in userForms:
                if i.startswith(type) and i[i.find('#') + 1:] == form:
                    embed=discord.Embed(title=userForms[i]['Name'], url=userForms[i]['Link'], description=userForms[i]['Desc'], color=0x2ca098)
                    embed.set_author(name=ctx.bot.user, icon_url=ctx.bot.user.display_avatar)
                    embed.set_thumbnail(url=userForms[i]['Image'])
                    await ctx.respond(embed=embed)
                    break
        elif by == 'Name':
            for i in userForms:
                if userForms[i]['Name'].casefold() == form.casefold():
                    embed=discord.Embed(title=userForms[i]['Name'], url=userForms[i]['Link'], description=userForms[i]['Desc'], color=0x2ca098)
                    embed.set_author(name=ctx.bot.user, icon_url=ctx.bot.user.display_avatar)
                    embed.set_thumbnail(url=userForms[i]['Image'])
                    await ctx.respond(embed=embed)
                    break
        else: await ctx.respond(f'no form found with selector:{by} and value:{form}', ephemeral=True)
    else: await ctx.respond(f'{owner} has no forms', ephemeral=True)

@bot.slash_command(guild_ids=[*guildids])
async def editform(
    ctx, 
    by: Option(str,'the selector used to get the form',choices=['Name', 'Id'],required=True),
    form: Option(str,'the form you want to get. ex: \'1\' or \'og gundam\'',required=True),
    type: Option(str,'the type of form to get',choices=["Gunpla", "Character", "Other"],required=True),
    inputfield: Option(str,'the field you want to edit', choices=["Name","Link","Desc",'Image'],required=True),
    inputdata: Option(str,'the data you want to set the input field to', required=True),
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
            if i.startswith(type) and i[i.find('#') + 1:] == form:
                userForms[i][inputfield] = inputdata
                await ctx.respond(f'{inputfield} changed to {inputdata} on {i}',ephemeral=True)
                break
    elif by == 'Name':
        for i in userForms:
            if userForms[i]['Name'].casefold() == form.casefold():
                userForms[i][inputfield] = inputdata
                await ctx.respond(f'{inputfield} changed to {inputdata} on {userForms[i]["Name"]}',ephemeral=True)
                break

@bot.slash_command(guild_ids=[*guildids])
@permissions.has_any_role(*adminRoles)
async def delkey(ctx, owner: Option(discord.Member,'the users forms to delete')):
    dataBaseKey = str(owner.id) + "'s forms"
    del db[dataBaseKey]
    await ctx.respond('key has been deleted', ephemeral=True)
@bot.slash_command(guild_ids=[*guildids])
@permissions.has_any_role(*adminRoles)
async def getkey(ctx, owner: Option(discord.Member,'the users forms to delete')):
    dataBaseKey = str(owner.id) + "'s forms"
    await ctx.respond(str(db[dataBaseKey]), ephemeral=True)


bot.run(token)

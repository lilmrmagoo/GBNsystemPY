import discord
from discord.commands import Option, permissions
import os
from replit import db
bot = discord.Bot()
token = os.environ['TOKEN']
adminRoles = ['helper','Moderators','Owner']
def findGapInIds(dict, type):
    lastid = 1
    for i in dict.keys():
        if i.startswith(type):
            currentid = int(i[i.find('#')+1])
            if currentid == lastid:
                lastid+=1
                continue
            else:
                return currentid
    return False
def countKeysWith(dict, type):
    dictKeys = dict.keys() 
    count = 0 
    for i in dictKeys:
        if i.startswith(type): 
            count+=1
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
    if (membersRoles.count(role) > 0):
        return True
    else: 
        return False

    

@bot.on_ready()
async def on_ready(self):
    print(f'system online logged in as {self}')


@bot.slash_command(guild_ids=[472944754397806619])
async def createform(
    ctx, 
    googledoc: Option(str, "the form link", required=True), 
    formtype: Option(str, "type of form", choices=["Gunpla","Character", "Other"], required=True),
    name: Option(str, "Name for character or gunpla", required=True),
    owner: Option(discord.Member, "The owner of the form", required=False)
):
    print('command createform activated')
    if (validGoogleDoc(googledoc)):
        if owner == None:
            owner = ctx.author
        dataBaseKey = str(owner.id) + "'s forms"
        if doesKeyExist(dataBaseKey):
            userForms = db.get(dataBaseKey)
            gap = findGapInIds(userForms, formtype)
            if gap == False:
                formId = countKeysWith(userForms, formtype) + 1
            else:
                formId = gap +1  
            userForms[f"{formtype}#{formId}"] = {"Name": name, "Link": googledoc, "Form Type": formtype}
            db[dataBaseKey] = userForms
        else:
            newDict = {"Name": name, "Link": googledoc, "Form Type": formtype}
            db[dataBaseKey] = {f"{formtype}#1":newDict}
        await ctx.respond(f"{owner}'s {formtype} has been created!")
        print(dataBaseKey)
        print(db[dataBaseKey])

    else:
        await ctx.respond('non valid link provided')
        print(owner)
@bot.slash_command(guild_ids=[472944754397806619])
async def deleteform(
    ctx, 
    by: Option(str,'the selector used to delete the form', choices=['Id','Name'], required=True),
    form: Option(str, 'the form you want to delete', required=True),
    owner: Option(discord.Member, 'the owner of the form', required=False)
):
    if owner == None:
        owner = ctx.author
    dataBaseKey = str(owner.id) + "'s forms"
    userForms = db[dataBaseKey]
    if by == 'Id'

@bot.slash_command(guild_ids=[472944754397806619])
@permissions.has_any_role(*adminRoles)
async def delkey(ctx, owner: Option(discord.Member, 'the users forms to delete')):
    dataBaseKey = str(owner.id) + "'s forms"
    del db[dataBaseKey]
    await ctx.respond('key has been deleted')
bot.run(token)
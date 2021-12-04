import discord
from discord.commands import Option, permissions
import os
from replit import db
bot = discord.Bot()
token = os.environ['TOKEN']



def validGoogleDoc(input):
    link = "https://docs.google.com/"
    if (input.startswith(link)):
        return True
    else:
        return False

def doesKeyExist(key):
    if db[key]: return True 
    else: return False
def userHasRole(member, role):
    membersRoles = member.roles
    if (membersRoles.count(role) > 0):
        return True
    else: 
        return False

    

#@bot.on_ready()
#async def on_ready():


@bot.slash_command(guild_ids=[472944754397806619], name= 'accept')
@permissions.has_any_role("helper", "Moderators", "Owner")
async def accept(
    ctx, 
    googledoc: Option(str, "the submission link", required=True), 
    submissiontype: Option(str, "type of submission", choices=["Gunpla","Character", "Other"]),
    submiter: Option(discord.Member, "the user who submited the submission"),
    name: Option(str, "Name for entry")
):
    print('command accepted activated')
    if (validGoogleDoc(googledoc)):
        dataBaseKey = str(submiter.id) + "'s forms"
        if doesKeyExist(dataBaseKey):
            pass
        else:
            newDict = {"Name": name, "Link": googledoc, "Form Type": submissiontype}
            db[dataBaseKey] = {name:newDict}
        print(submiter.id)

    else:
        await ctx.respond('no link provided')
        print(submiter)

bot.run(token)


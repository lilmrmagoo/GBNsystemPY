import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ui import InputText, Modal, View, Button
from replit import db
from shared import adminRoles, validation, guildIds, Confirm, Ranks

guildids = guildIds
def IntializeUser(user):
    key= f"{user.id}'s data'"
    if not validation.doesKeyExist(key):
        dict = {
            "Rank": 0,
            "Money": 0,
            "Rep": 0,
            "Forces": [],
            "Items": []
        }
        db[key] = dict
    userData = db[key]
    return userData
#probably pointless may be useful later idk
def getUserRoleRank(member):
    roles = member.roles
    rank = None
    for i in reversed(roles):
        print(i.name)
        if i.name.endswith("Rank"):
            print("rank found")
            rank = i
            break
    else:
        return None;
    return rank
def createPageView(user):
    view = PageView(timeout=300.0,disable_on_timeout=True)
    view.add_item(UserNavButton(user=user,label="Forms",page="forms"))
    view.add_item(UserNavButton(user=user,label="Info",page="info"))
    return view
def createListEmbed(user):
    dataBaseKey = str(user.id) + "'s forms"
    if validation.doesKeyExist(dataBaseKey):
        userForms = db.get(dataBaseKey)
        embed = discord.Embed(title=f"{user}'s forms", color=0x2ca098)
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
        return embed
def createUserEmbed(user, userData):
    embed = discord.Embed(title=f"{user.name}'s Info",color=0x2ca098)
    embed.set_thumbnail(url=user.avatar)
    embed.add_field(name="Join Date", value=user.joined_at.strftime("%x"))
    embed.add_field(name="Nickname", value=user.nick)
    rank = Ranks[userData["Rank"]]
    embed.add_field(name="Rank", value=f"{rank}-Rank")
    return embed
class PageView(View):
    def __init__(self, timeout=300,disable_on_timeout=True):
        super().__init__(timeout=timeout)
    async def on_timeout(self):
        self.clear_items()
        await self.interaction.edit_original_response(view=None)
    def set_interaction(self, interaction):
        self.interaction = interaction
class UserNavButton(Button):
    def __init__(self,page=None,user=None,label=None):
        super().__init__(label=label,style=discord.ButtonStyle.primary)
        self.page = page
        self.user = user
    async def callback(self, interaction: discord.Interaction):
        user = self.user
        response = interaction.response
        if self.page.casefold() == "forms":
            await response.edit_message(embed=createListEmbed(user))
        if self.page.casefold() == "info":
            await response.edit_message(embed=createUserEmbed(user))

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    user = SlashCommandGroup('user',"Commands to view a users info")

    @user.command(guild_ids=[*guildids], description='Get A users info')
    async def get(self,ctx,user: Option(discord.Member,"the person who's info you want to get", required=False, default=None)):
        if user == None:
            user = ctx.author
        userData = IntializeUser(user)
        view = createPageView(user)
        embed = createUserEmbed(user,userData)
        interaction = await ctx.respond(embed=embed, view=view)
        view.set_interaction(interaction)
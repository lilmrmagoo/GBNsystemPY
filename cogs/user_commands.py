import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ui import InputText, Modal, View, Button
from classes.user import User
from classes.form import Form
from shared import adminRoles, validation, guildIds, Confirm, Ranks

guildids = guildIds
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
    view.add_item(UserNavButton(discordUser=user,label="Forms",page="forms"))
    view.add_item(UserNavButton(discordUser=user,label="Info",page="info"))
    return view
def createListEmbed(title, user:User):
    userForms = user.listForms(Form.form_factory)
    embed = discord.Embed(title=title, color=0x2ca098)
    gunplas = ' '
    characters = ' '
    others = ' '
    for form in userForms:
        name = form.name
        if form.type == 'Gunpla':
            gunplas = f'{gunplas}\n{name}'
        elif form.type == 'Character':
            characters = f'{characters}\n{name}'
        elif form.type == 'Other':
            others = f'{others}\n{name}'
    
    if gunplas != ' ': embed.add_field(name='Gunpla Forms', value=gunplas)
    if characters != ' ': embed.add_field(name='Character Forms', value=characters)
    if others != ' ': embed.add_field(name='Other Forms',value=others,)
    return embed
def createUserEmbed(discordUser, userData):
    embed = discord.Embed(title=f"{discordUser.name}'s Info",color=0x2ca098)
    embed.set_thumbnail(url=discordUser.avatar)
    embed.add_field(name="Join Date", value=discordUser.joined_at.strftime("%x"))
    embed.add_field(name="Nickname", value=discordUser.nick)
    rank = userData.rank
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
    def __init__(self,page=None,discordUser=None,label=None):
        super().__init__(label=label,style=discord.ButtonStyle.primary)
        self.page = page
        self.discordUser = discordUser
        self.user = User.GetById(self.discordUser.id)
    async def callback(self, interaction: discord.Interaction):
        response = interaction.response
        if self.page.casefold() == "forms":
            await response.edit_message(embed=createListEmbed(f"{self.discordUser}'s Forms",self.user))
        if self.page.casefold() == "info":
            await response.edit_message(embed=createUserEmbed(self.discordUser,self.user))

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    user = SlashCommandGroup('user',"Commands to view a users info")

    @user.command(guild_ids=[*guildids], description='Get A users info')
    async def get(self,ctx,user: Option(discord.Member,"the person who's info you want to get", required=False, default=None)):
        DiscordUser = user
        if DiscordUser == None:
            DiscordUser = ctx.author
        print(DiscordUser.id, type(DiscordUser.id))
        user = User.GetById(DiscordUser.id)
        view = createPageView(DiscordUser)
        embed = createUserEmbed(DiscordUser,user)
        interaction = await ctx.respond(embed=embed, view=view)
        view.set_interaction(interaction)

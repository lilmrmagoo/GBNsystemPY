import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion
guildids = guildIds

class ViewCommands(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    view = SlashCommandGroup('view', 'commands to view forces characters or gunpla.', default_member_permissions=discord.Permissions(administrator=True)) 

    @force.command(guild_ids=[*guildids], description='view a force')
    async def force(ctx, self, name: Option(str,"the name of the force", required=True)):
        
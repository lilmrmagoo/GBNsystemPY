import discord
from discord.commands import CommandPermission, SlashCommandGroup
from discord.ext import commands

class ForceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    force = SlashCommandGroup('force', 'commands to edit or create forces.', 
        permissions=[
                CommandPermission(
                    "Owner", 2, True
                )
            ])

    @force.command(guild_ids=[479493485037355022,472944754397806619])
    async def hello(self, ctx):
        await ctx.respond("Hello, this is a slash subcommand from a cog!")


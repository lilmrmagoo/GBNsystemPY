import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion
from PIL import Image
guildids = guildIds

def merge(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im

class ViewCommands(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    view = SlashCommandGroup('view', 'commands to view forces characters or gunpla.', default_member_permissions=discord.Permissions(administrator=True)) 


    @view.command(guild_ids=[*guildids], description='view a force')
    async def force(ctx, self, name: Option(str,"the name of the force", required=True)):
        forceScreen = Image.open("force screen2.png")
        
        
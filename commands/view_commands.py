import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from replit import db
from shared import guildIds, validation, conversion
from PIL import Image, ImageDraw, ImageFont
import os
guildids = guildIds

def merge(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im

class ViewCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    view = SlashCommandGroup('view', 'commands to view forces characters or gunpla.', default_member_permissions=discord.Permissions(administrator=True)) 


    @view.command(guild_ids=[*guildids], description='view a force')
    async def force(self, ctx, name: Option(str,"the name of the force", required=True)):
        imageFolder = os.path.join(os.path.dirname( __file__ ), os.pardir, 'images')
        imagePath = os.path.join(imageFolder, "force screen2.png")
        fontFolder = os.path.join(os.path.dirname( __file__ ), os.pardir, 'fonts')
        fontPath = os.path.join(fontFolder, "Play-Regular.ttf")
        with Image.open(imagePath) as forceScreen:
            draw = ImageDraw.Draw(forceScreen)
            font = ImageFont.truetype(fontPath, size = 40)
            draw.text((490,115),"FORCE NAME", font = font)
            forceScreen.save(os.path.join(imageFolder,"Test1.png"))
        ImageFile = discord.File(os.path.join(imageFolder,"Test1.png"))
        await ctx.respond("force", file=ImageFile)
        
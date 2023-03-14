import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands
from shared import guildIds
from commands.force_commands import Force
from PIL import Image, ImageDraw, ImageFont
guildids = guildIds

def merge(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im

def fillTextBox():
    pass

# this is the function I wrote 
def getFontSize(fontpath,text,maxWidth,maxHeight,maxSize=150,minSize=1):
    bestSize = 0
    while int(minSize) <= maxSize:
        img = Image.new('RGB', (maxWidth, maxHeight), color='white')
        draw = ImageDraw.Draw(img)
        midSize = int((minSize+maxSize)/2)
        font = ImageFont.truetype(fontpath, size=midSize)
        bbox = draw.textbbox((1,1),text,font)
        if (bbox[2] - bbox[0]) > maxWidth or (bbox[3] - bbox[1]) > maxHeight:
            maxSize = midSize -1
        else: 
            bestSize = midSize
            minSize = midSize +1
    print(f"largest size: {bestSize}")
    return bestSize, bbox

class ViewCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    view = SlashCommandGroup('view', 'commands to view forces characters or gunpla.', default_member_permissions=discord.Permissions(administrator=True)) 


    @view.command(guild_ids=[*guildids], description='view a force')
    async def force(self, ctx, name: Option(str,"the name of the force", required=True)):
        force = Force.searchDatabase(name)
        if force == None: await ctx.respond("No force found with that name", ephermal = True)
        await ctx.defer()
        view = force.createPageView("Image")
        interaction = await ctx.respond(file=force.createInfoScreen(),view = view)
    @view.command(guild_ids=[*guildids], description='view a force')
    async def test(self, ctx, name: Option(str,"the name of the force", required=True)):
        force = Force.searchDatabase(name)
        if force == None: await ctx.respond("No force found with that name", ephermal = True)
        await ctx.defer()
        await ctx.respond(file=force.createMemberScreen())
        
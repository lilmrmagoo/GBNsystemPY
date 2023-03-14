from replit import db
import discord
import discord.ui
from PIL import Image, ImageDraw, ImageFont
adminRoles = ['helper', 'Moderators', 'Owner']
guildIds= [479493485037355022,472944754397806619]
Ranks = ['F','E','D','C','B','A','S','SS']

class PageView(discord.ui.View):
    def __init__(self, timeout=60,disable_on_timeout=True):
        super().__init__(timeout=timeout)
    async def on_timeout(self):
        await self.message.edit(view=None)
        #self.clear_items()
        #interaction = self.interaction
        #if isinstance(interaction,discord.WebhookMessage):
            #await interaction.edit(view=None,attachments =interaction.attachments)
        #else:await interaction.edit_original_response(view=None)
        #self.disable_all_items()



class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.interaction = None
    # When the confirm button is pressed, set the inner value
    # to `True` and stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.interaction = await interaction.response.send_message("Confirming...")
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.interaction = await interaction.response.send_message("Canceling...",ephemeral=True)
        self.value = False
        self.stop()
        

class validation():
    def validGoogleDoc(input):
        link = "https://docs.google.com/"
        if (input.startswith(link)):
            return True
        else:
            return False
    
    def validDiscordLink(input):
        link = "https://discord.com/"
        if (input.startswith(link)):
            return True
        else:
            return False
    def validHexColor(input):
        hexdigits = '0123456789abcdef'
        try:
            type(input) == type('')
        except:
            return False
        input = input.lstrip('#')
        if (len(input) == 6):
            for letter in input.casefold():
                if letter not in hexdigits:
                    return False
            return True
        else: return False
            
    def doesKeyExist(key):
        if db.prefix(key): return True
        else: return False
    def userHasRole(member, roles):
        hasRole = False
        membersRoles = member.roles
        for i in membersRoles:
            if i.name in roles:
                hasRole = True
        return hasRole
    def addFieldsToEmbed(dict, embed):
        defualtFields = ['Name', 'Desc','Link','Owner','Leader','Image','Colour','Ranking','Form Type','Members','RoleID','MemberCount', 'Stats', 'BaseStats','','ID', 'ServerID','NestID']
        for i in dict:
            if i not in defualtFields: 
                x = dict[i]
                inline = False
                if i.find('INLINE') != -1:
                    i = i.strip('#INLINE')
                    inline = True
                x = x.split("\\n")
                s = '\n'.join(x)
                embed.add_field(name=i, value=s, inline=inline)
        return embed
class conversion():
    def hexToRGB(hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

class ImageGeneration():
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
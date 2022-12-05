from replit import db
import discord
import discord.ui
adminRoles = ['helper', 'Moderators', 'Owner']
guildIds= [479493485037355022,472944754397806619]
Ranks = ['F','E','D','C','B','A','S','SS']

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
        defualtFields = ['Name', 'Desc','Link','Owner','Leader','Image','Colour','Ranking','Form Type','Members','RoleID','MemberCount', 'Stats', 'BaseStats','','ID']
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
from replit import db
adminRoles = ['helper', 'Moderators', 'Owner']
guildIds= [479493485037355022,472944754397806619]

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
    def userHasRole(member, role):
        membersRoles = member.roles
        if isinstance(role, str):
            if (membersRoles.count(role) > 0):
                return True
            else:
                return False
        elif isinstance(role, list):
            for i in role:
                if (membersRoles.count(i) > 0):
                    return True
            return False
    def addFieldsToEmbed(dict, embed):
        defualtFields = ['Name', 'Desc','Link','Owner','Leader','Image','Colour','Ranking','Form Type','Members']
        for i in dict:
            if i not in defualtFields: 
                embed.add_field(name=i, value=dict[i], inline=True)
        return embed
class conversion():
    def hexToRGB(hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
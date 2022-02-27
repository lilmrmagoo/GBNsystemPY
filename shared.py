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
        if (input.length == 6):
            for letter in input.casefold():
                if letter not in hexdigits:
                    return False
            return True
        else: return False
            
    def doesKeyExist(key):
        if db.prefix(key): return True
        else: return False
class conversion():
    def hexToRGB(hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
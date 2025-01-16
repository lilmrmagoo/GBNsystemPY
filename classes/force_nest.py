from classes.force import Force

class ForceNest:
    #if no id is supplied it generates a new one, making a completely different ForceNest
    def __init__(self,
                 Name: str,
                 Link: str,
                 Force: Force,
                 Size: str,
                 Desc: str = None,
                 Image: str = None,
                 Id: int = None):
        self.Name = Name
        self.Link = Link
        self.Force = Force
        self.Desc = Desc
        self.Image = Image
        self.Size = Size
        if Id == None: self.Id = ForceNest.generate_new_id()
        else: self.Id = Id

    def to_dict(self):
        exclude = ["self", "Force"]
        dict = {
            attr: getattr(self, attr)
            for attr in dir(self) if not callable(getattr(self, attr))
            and not attr.startswith("__") and attr not in exclude
        }
        dict["ForceName"] = self.Force.Name
        return dict

    def createEmbed(self):
        force = self.Force
        inlink = self.Link
        inimage = self.Image
        link = None
        image = None
        if validation.validGoogleDoc(inlink) or validation.validDiscordLink(
                inlink):
            link = inlink
        else:
            print(f'{inlink} is an invalid link')
            link = 'https://discord.com/channels/479493485037355022/591348299752013837/917927502872215552'
        if inimage.startswith('https') or inimage.startswith('http'):
            image = inimage
        else:
            image = 'https://cdn.discordapp.com/avatars/826265731930128394/ce7d79e6332e54a9a394b42cb182ddf7.png?size=4096'
        embed = discord.Embed(title=self.Name,
                              url=link,
                              description=self.Desc,
                              color=0x2ca098)
        embed.set_author(name=f"{force.Name}'s", icon_url=force.Image)
        embed.set_thumbnail(url=image)
        embed.add_field(name='Size', value=self.Size, inline=True)
        #embed = validation.addFieldsToEmbed(self.to_dict(), embed)
        return embed

    @staticmethod
    def generate_new_id():
        if not validation.doesKeyExist("IDs"):
            db["IDs"] = {}
            IDs = db["IDs"]
            IDs["LastNestID"] = 0
        else:
            IDs = db["IDs"]
        if "LastNestID" not in IDs.keys():
            IDs["LastNestID"] = 0
        return IDs["LastNestID"] + 1

    @staticmethod
    def searchDatabase(id):
        for nest in db["ForceNests"]:
            if nest["Id"] == id:
                force = Force.searchDatabase(nest["ForceName"])
                newdict = {**nest}
                del newdict["ForceName"]
                return ForceNest(Force=force, **newdict)
        else:
            return None

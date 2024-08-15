import discord
from shared import validation
class Force:
    def __init__(self,
                 Name: str,
                 Link: str,
                 Leader: int,
                 Desc: str = None,
                 Image: str = None,
                 Colour: str = None,
                 Ranking: int = 0,
                 MemberCount: int = 0,
                 Members: dict = [],
                 RoleID: int = 0,
                 ServerID: int = None,
                 NestID: int = None):
        #loops through arguments and sets them as attributes of the class
        args = locals()
        for k, v in args.items():
            if k == "self": continue
            if k.startswith("__"): continue
            setattr(self, k, v)

    #converts Force to dict for database purposes.
    def to_dict(self):
        return {
            attr: getattr(self, attr)
            for attr in dir(self) if not callable(getattr(self, attr))
            and not attr.startswith("__") and attr != "self"
        }

    #creates the members page embed for the force
    def createMemberEmbed(self):
        members = self.sortMembersByRole()
        forceName = self.Name
        embed = discord.Embed(title=f"{forceName}",
                              url=self.Link,
                              color=0x2ca098)
        for i in members.keys():
            list = []
            for j in members[i]:
                doc = members[i][j]
                list.append(f"[{j}]({doc})")
            finalString = '\n'.join(list)
            embed.add_field(name=f"{i}s", value=finalString, inline=False)
        return embed

    #creates the main page emebed for the force
    def createEmbed(self, owner):
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
        embed.set_author(name=f"{owner}'s", icon_url=owner.display_avatar)
        embed.set_thumbnail(url=image)
        embed.add_field(name='Leader', value=owner, inline=True)
        embed.add_field(name='Member Count',
                        value=self.MemberCount,
                        inline=True)
        embed = validation.addFieldsToEmbed(self.to_dict(), embed)
        return embed

    #saves the force to the database
    def createInfoScreen(self):
        imageFolder = os.path.join(os.path.dirname(__file__), os.pardir,
                                   'images')
        imageGeneratedFolder = os.path.join(imageFolder, 'generated')
        imagePath = os.path.join(imageFolder,
                                 "force screen no-text labels.png")
        generatedImagePath = os.path.join(imageGeneratedFolder, "force.png")
        fontFolder = os.path.join(os.path.dirname(__file__), os.pardir,
                                  'fonts')
        blockfontPath = os.path.join(fontFolder, "Blockletter.otf")
        playfontPath = os.path.join(fontFolder, "Play-Regular.ttf")
        force = self
        nameSize, namebbox = ImageGeneration.getFontSize(
            blockfontPath, force.Name, 290, 45)
        wrapWidth = 30
        if len(force.Desc) >= 800:
            wrapWidth = 60
        elif len(force.Desc) >= 500:
            wrapWidth = 40

        description = "\n".join(textwrap.wrap(force.Desc, width=wrapWidth))
        descSize, descbbox = ImageGeneration.getFontSize(playfontPath,
                                                         description,
                                                         340,
                                                         375,
                                                         minSize=12)
        #descProps = getFontSizeAI(fontPath,force.Desc,340,375)

        with Image.open(imagePath).convert("RGBA") as forceScreen:
            draw = ImageDraw.Draw(forceScreen)
            descFont = ImageFont.truetype(playfontPath, size=descSize)
            nameFont = ImageFont.truetype(blockfontPath, size=nameSize)
            nameycentered = int((45 - (namebbox[3] - namebbox[1])) / 2) + 98
            print(nameycentered)
            nameycentered = nameycentered if nameycentered > 0 else 95
            draw.text((485, nameycentered),
                      force.Name,
                      font=nameFont,
                      fill='#36CFCA')
            draw.text((60, 95), description, font=descFont, fill='#62FBDF')
            if len(force.Image) > 0:
                forceImg = Image.open(
                    BytesIO(requests.get(force.Image).content)).convert("RGBA")
                # Define the maximum size of the image
                max_width = 320
                max_height = 215

                # Calculate the new size of the image while maintaining the aspect ratio
                width, height = forceImg.size
                ratio = min(max_width / width, max_height / height)
                new_size = (int(width * ratio), int(height * ratio))
                # Resize the image
                resized_img = forceImg.resize(new_size)
                forceScreen.alpha_composite(
                    resized_img, (int(475 + (320 - new_size[0]) / 2), 235))
            forceScreen.save(generatedImagePath)
        return discord.File(generatedImagePath)

    def createMemberScreen(self):
        pass
        imageFolder = os.path.join(os.path.dirname(__file__), os.pardir,
                                   'images')
        imageGeneratedFolder = os.path.join(imageFolder, 'generated')
        imagePath = os.path.join(imageFolder, "force members screen.png")
        generatedImagePath = os.path.join(imageGeneratedFolder,
                                          "force-members.png")
        fontFolder = os.path.join(os.path.dirname(__file__), os.pardir,
                                  'fonts')
        blockfontPath = os.path.join(fontFolder, "Blockletter.otf")
        playfontPath = os.path.join(fontFolder, "Play-Regular.ttf")
        force = self
        sortedMembers = force.sortMembersByRole()
        slot = 0
        with Image.open(imagePath).convert("RGBA") as forceScreen:
            for role in sortedMembers.keys():
                roleSize, rolebbox = ImageGeneration.getFontSize(
                    blockfontPath, role, 92, 33)
                roleFont = ImageFont.truetype(blockfontPath, size=roleSize)
                roleheight = rolebbox[3] - rolebbox[1]
                roleoffset = max(0, ((33 - roleheight) / 2))
                for member in sortedMembers[role].keys():
                    yrole = ((slot * 55) + 90) + roleoffset
                    xrole = (math.floor(slot / 7) * 405) + 85
                    nameSize, namebbox = ImageGeneration.getFontSize(
                        blockfontPath, member, 188, 33, maxSize=50)
                    nameFont = ImageFont.truetype(blockfontPath, size=nameSize)
                    nameheight = namebbox[3] - namebbox[1]
                    nameoffset = max(0, ((33 - nameheight) / 2))
                    yname = ((slot * 55) + 90) + nameoffset - 15
                    print(yname, nameoffset)
                    xname = (math.floor(slot / 7) * 405) + 85 + 92 + 5
                    draw = ImageDraw.Draw(forceScreen)
                    draw.text((xrole, yrole),
                              role,
                              font=roleFont,
                              fill='#36CFCA')
                    draw.text((xname, yname),
                              member,
                              font=nameFont,
                              fill='#62FBDF')
                    forceScreen.save(generatedImagePath)
                    slot += 1
        return discord.File(generatedImagePath)

    def save(self):
        forces = db["Forces"]
        for i in forces:
            if i["Name"] == self.Name:
                forces[forces.index(i)] = self.to_dict()
                break
        else:
            return None

    #searches the database for the force by name then returns the object
    def sortMembersByRole(self):
        roles = []
        sorted = {}
        for i in self.Members:
            role = i['Role']
            name = i['Name']
            doc = i['Doc']
            if role in roles:
                sorted[role][name] = doc
            else:
                roles.append(role)
                sorted[role] = {name: doc}
        return sorted

    def createPageView(self, type=None):
        view = PageView(timeout=300.0, disable_on_timeout=True)
        numofPages = 0
        if self.Members != []:
            view.add_item(
                ForceNavButton(force=self,
                               label="Members",
                               page="characters",
                               display_type=type))
            numofPages += 1
        if self.NestID != None and type == None:
            view.add_item(
                ForceNavButton(force=self,
                               label="Force Nest",
                               page="nest",
                               display_type=type))
            numofPages += 1
        if numofPages > 0:
            view.add_item(
                ForceNavButton(force=self,
                               label="Info",
                               page="info",
                               display_type=type))
        return view

    def getForceNest(self):
        return ForceNest.searchDatabase(self.NestID)

    @staticmethod
    def searchDatabase(name, Strict=False):
        if not Strict:
            for i in db["Forces"]:
                if i["Name"].casefold().startswith(name.casefold()):
                    return Force(**i)
            else:
                return None
        else:
            for i in db["Forces"]:
                if i["Name"] == name: return Force(**i)
            else:
                return None
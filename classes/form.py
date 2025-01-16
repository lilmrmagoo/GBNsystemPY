from connection import Connection
from classes.user import User
from shared import validation
import discord
class Form:
    def __init__(self,id,user_id:int,name:str,type:str,link:str|None,image:str|None,desc:str|None) -> None:
        if type in ("Gunpla","Character","Other"):
            self.type = type
        else:
            raise Exception("Invalid type for form")
        self.user = User.GetById(user_id)
        self.id = id
        self.user_id = user_id
        self.name = name
        self.link = link
        self.image = image
        self.desc = desc
        
    async def createEmbed(self,guild:discord.guild):
        inlink = self.link
        inimage = self.image
        discord_user = await guild.fetch_member(self.owner.discord_id)
        if validation.validGoogleDoc(inlink) or validation.validDiscordLink(
                inlink):
            link = inlink
        else:
            link = 'https://discord.com/channels/479493485037355022/591348299752013837/917927502872215552'
        if inimage.startswith('http'):
            image = inimage
        else:
            image = 'https://cdn.discordapp.com/avatars/826265731930128394/ce7d79e6332e54a9a394b42cb182ddf7.png?size=4096'
        embed = discord.Embed(title=self.name,
                            url=link,
                            description=self.desc,
                            color=0x2ca098)
        embed.set_author(name=f"{discord_user}'s", icon_url=discord_user.display_avatar)
        embed.set_thumbnail(url=image)
        embed.set_footer(text=self.id)
        #embed = validation.addFieldsToEmbed(dict, embed)
        return embed
    def AddToDb(self):
        sql = "insert into forms(user_id,name,link,type,image,desc) values (?,?,?,?,?,?)" 
        with Connection() as db:
            db.execute(sql, (self.user_id,self.name,self.link,self.type,self.image,self.desc))
            return True
    def updateInDb(self):
        sql = "update forms set name = ?, link = ?, type = ?, image = ?, desc = ? where id = ?"
        with Connection as db:
            db.execute(sql, (self.name, self.link, self.type, self.image, self.desc, self.id))
            return True
    @staticmethod
    def form_factory(cursor, row):
        fields = [column[0] for column in cursor.description]
        return Form(**{key: value for key, value in zip(fields, row)})
    @staticmethod
    def SearchDbByName(name,Strict=False):
        if Strict:
            sql = "select id,user_id,name,link,type,image,desc from forms where name = ?" 
        else:
            sql = "select id,user_id,name,link,type,image,desc from forms where name like ?%"
        with Connection as db:
            cursor = db.cursor()
            cursor.execute(sql,(name))
            row = cursor.fetchone()
            if row is not None:
                owner = User.searchById(row["user_id"])
                if owner is not None:
                    return Form(**row)
                else:
                    raise Exception("Form has no owner, Somehow, db shouldn't allow that.")
            else: return None
    @staticmethod
    def SearchDbByUser(user_id,max=30):
        sql = "select id,name,link,type,image,desc from forms where user_id = ? "
        if max is not None:
            sql += f"limit {max}"
        with Connection as db:
            db.row_factory = Form.form_factory
            cursor = db.cursor()
            cursor.execute(sql,(user_id))
            forms = cursor.fetchall()
            return forms


from connection import Connection
class User:
    def __init__(self,discord_id,id,rank,money,rep) -> None:
        self.id = id
        self.discord_id = discord_id
        self.rank = rank
        self.money = money
        self.rep = rep
    @staticmethod
    def GetByDiscordId(discord_id):
        sql = "select id, discord_id, rank, money, rep from users where discord_id = ?"
        with Connection() as db:
            row = None
            while row is None:
                cursor = db.cursor()
                cursor.execute(sql, (discord_id))
                row = cursor.fetchone()
                if row is not None:
                    return User(**row)
                else:
                    db.execute("insert into users(discord_id) values (?)", (discord_id))
    @staticmethod
    def searchById(id):
        sql = "select id, rank, money, rep, discord_id from users where id = ?"
        with Connection as db:
            cursor = db.cursor()
            cursor.execute(sql, (id))
            row = cursor.fetchone()
            if row is not None:
                return User(**row)
            else:
                return None
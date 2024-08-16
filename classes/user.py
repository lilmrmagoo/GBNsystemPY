from connection import Connection
class User:
    def __init__(self,discord_id,id,rank,money,rep) -> None:
        self.id = id
        self.rank = rank
        self.money = money
        self.rep = rep
    @staticmethod
    def GetById(discord_id):
        sql = "select id, rank, money, rep from users where id = ?"
        with Connection() as db:
            row = None
            while row is None:
                cursor = db.cursor()
                cursor.execute(sql, (discord_id))
                row = cursor.fetchone()
                if row is not None:
                    return User(**row)
                else:
                    db.execute("insert into users(id) values (?)", (discord_id))
    @staticmethod
    def searchById(id):
        sql = "select id, rank, money, rep, id from users where id = ?"
        with Connection as db:
            cursor = db.cursor()
            cursor.execute(sql, (id))
            row = cursor.fetchone()
            if row is not None:
                return User(**row)
            else:
                return None
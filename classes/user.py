from connection import Connection
class User:
    def __init__(self,id,rank,money,rep) -> None:
        self.id = id
        self.rank = rank
        self.money = money
        self.rep = rep
    def AddToDb(self):
        sql = "insert into users(id,rank, money, rep) (?, COALESCE(?, DEFAULT), COALESCE(?, DEFAULT), COALESCE(?, DEFAULT)" 
        with Connection() as db:
            db.execute(sql, (self.id,self.name,self.rank,self.money,self.rep))
            return True        
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
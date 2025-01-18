import sqlite3

class Connection:
    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None
        sqlite3.enable_callback_tracebacks(True)

    def __enter__(self):
        def dict_factory(cursor, row):
            fields = [column[0] for column in cursor.description]
            return {key: value for key, value in zip(fields, row)}
        self.conn = sqlite3.connect("GBN.db")
        self.conn.row_factory = dict_factory
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
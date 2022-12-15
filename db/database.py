import sqlite3 as sq


class DataBase:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(DataBase)
            return cls.instance
        return cls.instance

    def __init__(self, db_name='db/database.db'):
        self.name = db_name
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        try:
            return sq.connect(self.name)
        except sq.Error:
            pass

    def get_data(self, table: str) -> list:
        self.cursor.execute(f'SELECT * FROM {table}')
        return self.cursor.fetchall()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


db = DataBase()

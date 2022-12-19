import sqlite3 as sq


class DataBase:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(DataBase)
            return cls.instance
        return cls.instance

    def __init__(self, db_name='tgbot/db/database.db'):
        self.name = db_name
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def connect(self):
        try:
            return sq.connect(self.name)
        except sq.Error:
            return 'Ошибка соединения'

    def get_data(self, **kwargs) -> list:
        if 'where' in kwargs:
            if kwargs['where'] == 1:
                self.cursor.execute(f"SELECT * FROM {kwargs['table']} WHERE {kwargs['operand1']} = {kwargs['operand2']}")
            if kwargs['where'] == 2:
                self.cursor.execute(f"SELECT * FROM {kwargs['table']} WHERE {kwargs['operand1']} = {kwargs['operand2']} AND {kwargs['operand3']} = {kwargs['operand4']}")
        else:
            self.cursor.execute(f"SELECT * FROM {kwargs['table']}")
        return self.cursor.fetchall()

    def working_with_basket(self, **kwargs):
        answer = ''
        count_entries = 0
        is_delete = False
        self.cursor.execute(f'SELECT `count` FROM basket WHERE user_id = {kwargs["user_id"]} AND product_id = {kwargs["product_id"]}')
        entry = self.cursor.fetchall()
        if len(entry) > 0:
            count_entries = entry[0][0]
        if kwargs['state'] == 'add_basket_count':
            self.cursor.execute(f'INSERT INTO basket(user_id, product_id, `count`) VALUES ({kwargs["user_id"]}, {kwargs["product_id"]} , 1)')
            answer = 'Продукт успешно добавлен.'
        elif kwargs['state'] == 'inc_basket_count':
            self.cursor.execute(f'UPDATE basket SET `count` = `count` + 1 WHERE user_id = {kwargs["user_id"]} AND product_id = {kwargs["product_id"]}')
            answer = f'Продукт успешно добавлен, всего: {count_entries + 1}'
        elif kwargs['state'] == 'dec_basket_count':
            if count_entries > 1:
                self.cursor.execute(f'UPDATE basket SET `count` = `count` - 1 WHERE user_id = {kwargs["user_id"]} AND product_id = {kwargs["product_id"]}')
                answer = f'Продукт успешно удалён, всего: {count_entries - 1}'
            else:
                self.cursor.execute(f'DELETE FROM basket WHERE user_id = {kwargs["user_id"]} AND product_id = {kwargs["product_id"]}')
                answer = 'Продукт успешно удалён.'
                is_delete = True
        self.conn.commit()
        return answer, is_delete


db = DataBase()

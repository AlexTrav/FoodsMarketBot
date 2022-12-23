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
        if 'where' in kwargs and 'get_name_product' not in kwargs:
            if kwargs['where'] == 1:
                self.cursor.execute(f"SELECT * FROM {kwargs['table']} WHERE {kwargs['operand1']} = {kwargs['operand2']}")
            if kwargs['where'] == 2:
                self.cursor.execute(f"SELECT * FROM {kwargs['table']} WHERE {kwargs['operand1']} = {kwargs['operand2']} AND {kwargs['operand3']} = {kwargs['operand4']}")
        elif 'get_name_product' in kwargs:
            if 'field1' in kwargs and 'field2' in kwargs:
                self.cursor.execute(f"SELECT {kwargs['field1']}, {kwargs['field2']} FROM products WHERE id = {kwargs['operand1']}")
            elif 'field1' in kwargs:
                self.cursor.execute(f"SELECT {kwargs['field1']} FROM products WHERE id = {kwargs['operand1']}")
        else:
            self.cursor.execute(f"SELECT * FROM {kwargs['table']}")
        return self.cursor.fetchall()

    def check_user(self, **kwargs):
        self.cursor.execute('SELECT * FROM users')
        users = self.cursor.fetchall()
        for user in users:
            if kwargs['user_id'] not in user:
                self.cursor.execute(f'INSERT INTO users(id) VALUES ({kwargs["user_id"]})')
                self.conn.commit()

    def add_balance(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET balance = balance + 10000 WHERE id = {kwargs["user_id"]}')
        self.conn.commit()

    def check_enough_money(self, **kwargs):
        self.cursor.execute(f'SELECT balance FROM users WHERE id = {kwargs["user_id"]}')
        return self.cursor.fetchall()[0][0] >= kwargs['sum']

    def check_address(self, **kwargs):
        self.cursor.execute(f'SELECT address FROM users WHERE id = {kwargs["user_id"]}')
        tmp = self.cursor.fetchall()
        return tmp[0][0] is not None

    def update_address(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET address = "{kwargs["address"]}" WHERE id = {kwargs["user_id"]}')
        self.conn.commit()

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

    def working_with_place_an_order(self, **kwargs):
        if 'insert_in_orders' in kwargs:
            self.cursor.execute(f'INSERT INTO orders(user_id, reg_date) VALUES ({kwargs["user_id"]}, {kwargs["date"]})')
        if 'insert_in_orders_total_cost' in kwargs:
            self.cursor.execute(f'UPDATE orders SET total_cost = {kwargs["total_cost"]} WHERE id = {kwargs["order_id"]} AND user_id = {kwargs["user_id"]}')
        if 'insert_in_order_items' in kwargs:
            self.cursor.execute(f'INSERT INTO order_items(order_id, user_id, product_id, `count`, cost) VALUES ({kwargs["order_id"]}, {kwargs["user_id"]}, {kwargs["product_id"]}, {kwargs["count"]}, {kwargs["cost"]})')
        if 'clear_basket' in kwargs:
            self.cursor.execute(f'DELETE FROM basket WHERE user_id = {kwargs["user_id"]}')
        self.conn.commit()

    def order_payment(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET balance = balance - {kwargs["sum"]} WHERE id = {kwargs["user_id"]}')
        self.cursor.execute(f'UPDATE orders SET is_paid = 1 WHERE id = {kwargs["order_id"]}')
        self.conn.commit()


db = DataBase()

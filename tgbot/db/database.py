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


#######################################################################USER#########################################################################################

    def check_user(self, **kwargs):
        self.cursor.execute('SELECT * FROM users')
        users = self.cursor.fetchall()
        if not users:
            self.cursor.execute(f'INSERT INTO users(id) VALUES ({kwargs["user_id"]})')
            self.conn.commit()
        else:
            self.cursor.execute(f'SELECT * FROM users WHERE id = {kwargs["user_id"]}')
            user = self.cursor.fetchall()
            if not user:
                self.cursor.execute(f'INSERT INTO users(id) VALUES ({kwargs["user_id"]})')
                self.conn.commit()

    def check_role(self, **kwargs):
        self.cursor.execute(f'SELECT * FROM workers WHERE id = {kwargs["user_id"]} AND role_id = {kwargs["role_id"]}')
        workers = self.cursor.fetchall()
        if workers:
            self.cursor.execute(f'UPDATE users SET role_id = {kwargs["role_id"]} WHERE id = {kwargs["user_id"]}')
            self.conn.commit()
            if kwargs['role_id'] == 2:
                return 'Вы вошли как оператор'
            if kwargs['role_id'] == 3:
                return 'Вы вошли как курьер'
            if kwargs['role_id'] == 4:
                return 'Вы вошли как админ'
        else:
            return 'Вас нету в списке работников!'

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

    def update_phone(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET phone_number = "{kwargs["phone"]}" WHERE id = {kwargs["user_id"]}')
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
        if 'insert_in_delivery' in kwargs:
            self.cursor.execute(f'INSERT INTO delivery(order_id) VALUES ({kwargs["order_id"]})')
        if 'clear_basket' in kwargs:
            self.cursor.execute(f'DELETE FROM basket WHERE user_id = {kwargs["user_id"]}')
        self.conn.commit()

    def order_payment(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET balance = balance - {kwargs["sum"]} WHERE id = {kwargs["user_id"]}')
        self.cursor.execute(f'UPDATE orders SET is_paid = 1 WHERE id = {kwargs["order_id"]}')
        self.conn.commit()

    def get_role_id(self, **kwargs):
        self.cursor.execute(f'SELECT role_id FROM users WHERE id = {kwargs["user_id"]}')
        role_id = self.cursor.fetchall()[0][0]
        return role_id

    def exit_role(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET role_id = 1 WHERE id = {kwargs["user_id"]}')
        self.conn.commit()

    def get_search_answer(self, **kwargs):
        self.cursor.execute(f'SELECT * FROM products WHERE `name_lc` LIKE "%{kwargs["search_query"].lower()}%" AND `count` > 0')
        search_answer = self.cursor.fetchall()
        return search_answer

    def update_count_basket(self, **kwargs):
        self.cursor.execute(f'UPDATE basket SET `count` = {kwargs["count_stock"]} WHERE id = {kwargs["basket_id"]}')
        self.conn.commit()

    def update_count_product(self, **kwargs):
        for entry in db.get_data(table='basket', where=1, operand1='user_id', operand2=kwargs['user_id']):
            self.cursor.execute(f'UPDATE products SET `count` = `count` - {entry[3]} WHERE id = {entry[2]}')
            self.conn.commit()


#######################################################################ADMIN#######################################################################################


#######################################################################OPERATOR####################################################################################

    def product_change_price(self, **kwargs):
        self.cursor.execute(f'UPDATE products SET cost = {kwargs["new_price"]} WHERE id = {kwargs["product_id"]}')
        self.conn.commit()


    def product_change_count(self, **kwargs):
        self.cursor.execute(f'UPDATE products SET `count` = `count` + {kwargs["new_count"]}  WHERE id = {kwargs["product_id"]}')
        self.conn.commit()

    def insert_documents(self, **kwargs):
        self.cursor.execute(f'INSERT INTO documents(user_id, product_id, invoice_date, `count`, cost, invoice_number)'
                            f' VALUES ({kwargs["user_id"]}, {kwargs["product_id"]}, {kwargs["invoice_date"]}, {kwargs["count"]}, {kwargs["cost"]}, {kwargs["invoice_number"]})')
        self.conn.commit()

#######################################################################COURIER#####################################################################################

    def delivered_order(self, **kwargs):
        self.cursor.execute(f'UPDATE delivery SET worker_id = {kwargs["user_id"]}, is_completed = 1 WHERE order_id = {kwargs["order_id"]}')
        self.conn.commit()
        self.cursor.execute(f'UPDATE orders SET is_delivered = 1 WHERE id = {kwargs["order_id"]}')
        self.conn.commit()


#######################################################################DB-OBJECT###################################################################################

db = DataBase()

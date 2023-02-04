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
        if 'where' in kwargs and 'order_by' in kwargs:
            self.cursor.execute(f"SELECT * FROM {kwargs['table']} WHERE {kwargs['operand1']} = {kwargs['operand2']} ORDER BY {kwargs['operand3']} DESC")
        elif 'where' in kwargs and 'get_name_product' not in kwargs and 'order_by' not in kwargs:
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
            self.cursor.execute(f'INSERT INTO users(id, user_name) VALUES ({kwargs["user_id"]}, "{kwargs["user_name"]}")')
            self.conn.commit()
        else:
            self.cursor.execute(f'SELECT * FROM users WHERE id = {kwargs["user_id"]}')
            user = self.cursor.fetchall()
            if not user:
                self.cursor.execute(f'INSERT INTO users(id, user_name) VALUES ({kwargs["user_id"]}, "{kwargs["user_name"]}")')
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
        self.cursor.execute(f'INSERT INTO documents(product_id, doc_type_id, invoice_date, `count`, invoice_number) '
                            f'VALUES ({kwargs["user_id"]}, 4, {kwargs["invoice_date"]}, 0, {kwargs["invoice_number"]})')
        self.conn.commit()

    def get_document_user(self, **kwargs):
        self.cursor.execute(f'SELECT * FROM documents WHERE user_id IS NULL AND product_id = {kwargs["user_id"]} AND cost IS NULL')
        document_user = self.cursor.fetchall()
        return document_user

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

#######################################################################OPERATOR####################################################################################

    def product_change_price(self, **kwargs):
        self.cursor.execute(f'UPDATE products SET cost = {kwargs["new_price"]} WHERE id = {kwargs["product_id"]}')
        self.conn.commit()


    def product_change_count(self, **kwargs):
        if 'arrival_product' in kwargs:
            self.cursor.execute(f'UPDATE products SET `count` = `count` + {kwargs["new_count"]}  WHERE id = {kwargs["product_id"]}')
        if 'write_off_product' in kwargs:
            self.cursor.execute(f'UPDATE products SET `count` = `count` - {kwargs["write_off_count"]}  WHERE id = {kwargs["product_id"]}')
        self.conn.commit()

    def insert_documents(self, **kwargs):
        if 'arrival_product' in kwargs:
            self.cursor.execute(f'INSERT INTO documents(user_id, product_id, invoice_date, `count`, cost, invoice_number)'
                                f' VALUES ({kwargs["user_id"]}, {kwargs["product_id"]}, {kwargs["invoice_date"]}, {kwargs["count"]}, {kwargs["cost"]}, {kwargs["invoice_number"]})')
        if 'write_off_product' in kwargs:
            self.cursor.execute(f'INSERT INTO documents(user_id, product_id, doc_type_id, invoice_date, `count`, cost, invoice_number)'
                                f' VALUES ({kwargs["user_id"]}, {kwargs["product_id"]}, 2, {kwargs["invoice_date"]}, {kwargs["count"]}, {kwargs["cost"]}, {kwargs["invoice_number"]})')

        self.conn.commit()

    def get_unique_subcategories_ids(self):
        self.cursor.execute(f'SELECT subcategory_id FROM products')
        subcategories_ids = self.cursor.fetchall()
        unique_subcategories_ids = []
        for subcategory_id in subcategories_ids:
            if subcategory_id[0] not in unique_subcategories_ids:
                unique_subcategories_ids.append(subcategory_id[0])
        return unique_subcategories_ids

    def insert_product(self, **kwargs):
        self.cursor.execute(f'INSERT INTO products(subcategory_id, `name`, producing_country, brand, description, cost, photo, name_lc) VALUES ({kwargs["subcategory_id"]}, "{kwargs["name"]}", "{kwargs["producing_country"]}", "{kwargs["brand"]}", "{kwargs["description"]}", {kwargs["cost"]}, "{kwargs["photo"]}", "{kwargs["name"].lower()}")')
        self.conn.commit()

    def get_id(self, **kwargs):
        self.cursor.execute(f'SELECT `id` FROM products WHERE `name` = "{kwargs["name"]}"')
        pr_id = self.cursor.fetchall()[0][0]
        return pr_id

    def get_subcategory(self, **kwargs):
        self.cursor.execute(f'SELECT subcategory_name FROM subcategories_products WHERE id = {kwargs["subcategory_id"]}')
        subcategory_name = self.cursor.fetchall()[0][0]
        return subcategory_name

#######################################################################COURIER#####################################################################################

    def delivered_order(self, **kwargs):
        self.cursor.execute(f'UPDATE delivery SET worker_id = {kwargs["user_id"]}, is_completed = 1 WHERE order_id = {kwargs["order_id"]}')
        self.conn.commit()
        self.cursor.execute(f'UPDATE orders SET is_delivered = 1 WHERE id = {kwargs["order_id"]}')
        self.conn.commit()


#######################################################################ADMIN#######################################################################################

    def is_roles(self, **kwargs):
        is_operator, is_courier, is_admin = False, False, False
        self.cursor.execute(f'SELECT role_id FROM workers WHERE id = {kwargs["user_id"]}')
        for entry in self.cursor.fetchall():
            if entry[0]:
                if entry[0] == 2:
                    is_operator = True
                elif entry[0] == 3:
                    is_courier = True
                elif entry[0] == 4:
                    is_admin = True
        return is_operator, is_courier, is_admin

    def working_with_roles(self, **kwargs):
        if kwargs['action'] == 'del_role_operator':
            self.cursor.execute(f'DELETE FROM workers WHERE id = {kwargs["user_id"]} AND role_id = 2')
        if kwargs['action'] == 'del_role_courier':
            self.cursor.execute(f'DELETE FROM workers WHERE id = {kwargs["user_id"]} AND role_id = 3')
        if kwargs['action'] == 'del_role_admin':
            self.cursor.execute(f'DELETE FROM workers WHERE id = {kwargs["user_id"]} AND role_id = 4')
        if kwargs['action'] == 'add_role_operator':
            self.cursor.execute(f'INSERT INTO workers(id, role_id) VALUES ({kwargs["user_id"]}, 2)')
        if kwargs['action'] == 'add_role_courier':
            self.cursor.execute(f'INSERT INTO workers(id, role_id) VALUES ({kwargs["user_id"]}, 3)')
        if kwargs['action'] == 'add_role_admin':
            self.cursor.execute(f'INSERT INTO workers(id, role_id) VALUES ({kwargs["user_id"]}, 4)')
        self.conn.commit()


    def update_balance(self, **kwargs):
        self.cursor.execute(f'UPDATE users SET balance = balance + {kwargs["sum"]} WHERE id = {kwargs["user_id"]}')
        self.conn.commit()


    def insert_documents_add_balance(self, **kwargs):
        self.cursor.execute(f'INSERT INTO documents(user_id, product_id, doc_type_id, invoice_date, `count`, cost, invoice_number)'
                            f' VALUES ({kwargs["admin_user_id"]}, {kwargs["user_id"]}, 3, {kwargs["invoice_date"]}, 0, {kwargs["add_balance_sum"]}, {kwargs["invoice_number"]})')
        self.conn.commit()

    def update_documents_add_balance(self, **kwargs):
        self.cursor.execute(f'UPDATE documents SET user_id = {kwargs["admin_user_id"]}, cost = {kwargs["add_balance_sum"]}, doc_type_id = 3 WHERE id = {kwargs["doc_id"]}')
        self.conn.commit()

    def get_doc_type_id(self, **kwargs):
        self.cursor.execute(f'SELECT doc_type_id FROM documents WHERE id = {kwargs["doc_id"]}')
        doc_type_id = self.cursor.fetchall()[0][0]
        return doc_type_id


#######################################################################DB-OBJECT###################################################################################

db = DataBase()

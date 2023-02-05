from tgbot.db.database import db


def get_token_api() -> str:
    return db.get_data(table='config')[0][0]


class Documents:

    new_count = 0
    new_price = ''

    write_off_count = 0


class Products:

    subcategory_id = ''

    sorting = ''


class Users:

    id = ''


class MainPage:

    entries = 10

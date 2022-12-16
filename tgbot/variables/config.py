from tgbot.db.database import db


def get_token_api() -> str:
    return db.get_data(table='config')[0][0]

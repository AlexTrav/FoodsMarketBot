from db.database import db


def get_token_api():
    return db.get_data('config')[0][0]


TOKEN_API = get_token_api()



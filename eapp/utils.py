import hashlib
from models import Account, CanHo
from __init__ import app, db


def load_canho(kw=None):
    query = CanHo.query

    if kw:
        query = query.filter(CanHo.ma_can_ho.contains(kw))

    return query.all()


def get_canho_by_id(canho_id):
    return CanHo.query.get(canho_id)


def get_user_by_id(user_id):
    return Account.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = str(password)
        hash_pass = hashlib.md5(password.encode('utf-8')).hexdigest()

        return Account.query.filter(Account.username == username,
                                    Account.password == hash_pass).first()

    return None


def add_user(name, username, password):
    password = str(password)
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

    user = Account(name=name,
                   username=username,
                   password=password_hash,
                   user_type='customer')

    db.session.add(user)
    db.session.commit()

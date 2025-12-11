from models import CanHo
from __init__ import app

def load_canho(kw=None):
    query = CanHo.query

    if kw:
        query = query.filter(CanHo.ma_can_ho.contains(kw))

    return query.all()

def get_canho_by_id(canho_id):
    return CanHo.query.get(canho_id)
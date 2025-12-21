import hashlib
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from models import Account, Customer, CanHo, DatPhong, LoaiCanHo, PhoneNumber
from __init__ import app, db


def load_canho(kw=None, loai_canho_id=None):
    query = CanHo.query

    if kw:
        query = query.filter(CanHo.ma_can_ho.contains(kw))
    # loai_canho_id su dung cho tim kiem bang loai phong
    if loai_canho_id:
        query = query.filter(CanHo.id_loai_can_ho.__eq__(loai_canho_id))
    return query.all()


def get_canho_by_id(canho_id):
    return CanHo.query.get(canho_id)


def load_loai_canho():
    return LoaiCanHo.query.all()


def get_user_by_id(user_id):
    return Account.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = str(password)
        hash_pass = hashlib.md5(password.encode('utf-8')).hexdigest()

        return Account.query.filter(Account.username == username,
                                    Account.password == hash_pass).first()

    return None


def add_user(name, phone, username, password):
    password = str(password.strip())
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

    user = Customer(name=name.strip(),
                    phone=PhoneNumber(phone=str(phone)),
                    username=username.strip(),
                    password=password_hash,
                    user_type='customer')

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as ex:
        db.session.rollback()
        msg=str(ex.orig).lower()
        if 'username' in msg:
            raise Exception('Tên đăng nhập đã tồn tại')
        if 'phone' in msg:
            raise Exception('Số điện thoại đã được sử dụng')

        raise Exception('Dữ liệu không hợp lệ')


def add_booking(user_id, canho_id, ngay_nhan, thoi_han):
    try:
        # Xử lý ngày tháng về dạng chuẩn
        if isinstance(ngay_nhan, str):
            ngay_nhan_obj = datetime.strptime(ngay_nhan, '%Y-%m-%d')
        else:
            ngay_nhan_obj = ngay_nhan
        booking = DatPhong(
            customer_id=user_id,
            canho_id=canho_id,
            ngay_nhan=ngay_nhan_obj,
            thoi_han=thoi_han,
        )
        db.session.add(booking)
        db.session.commit()
        return True
    except Exception as ex:
        print(f"Lỗi lưu đặt phòng: {ex}")
        return False

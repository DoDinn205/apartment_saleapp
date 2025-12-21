from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from __init__ import db, app
from datetime import datetime

import enum


class ApartmentStatus(enum.Enum):
    CONTRONG = 1
    DANGTHUE = 2
    BAOTRI = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class LoaiCanHo(BaseModel):
    __tablename__ = 'loai_can_ho'
    name = Column(String(50), nullable=False)
    apartments = relationship('CanHo', backref='apartment_type', lazy=True)

    def __str__(self):
        return self.name


class Account(BaseModel, UserMixin):
    __tablename__ = "account"
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    # Một tài khoản chỉ có 1 sdt
    phone = relationship('PhoneNumber', backref='account', lazy=True, uselist=False)
    # Cột này để phân bệt loại tài khoản (Admin hay Customer)
    user_type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'account',
        'polymorphic_on': user_type
    }

    def __str__(self):
        return self.name


class Admin(Account):
    __tablename__ = "admin"
    user_id = Column(Integer, ForeignKey(Account.id), primary_key=True, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __str__(self):
        return self.name


class Customer(Account):
    __tablename__ = "customer"

    user_id = Column(Integer, ForeignKey(Account.id), primary_key=True, nullable=False)
    is_renting = Column(Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    def __str__(self):
        return self.name


class PhoneNumber(BaseModel):
    __tablename__ = "phone_number"

    phone = Column(String(12), nullable=False, unique=True)
    type = Column(String(50), nullable=False, default='Cell Phone')
    # 1 sdt chỉ thuộc về 1 tài khoản
    user_id = Column(Integer, ForeignKey(Account.id), nullable=False, unique=True)

    def __str__(self):
        return self.phone


class CanHo(BaseModel):
    __tablename__ = "can_ho"

    ma_can_ho = Column(String(50), nullable=False, unique=True)
    gia_thue = Column(Float, default=0)
    dien_tich = Column(Float, default=0)
    trang_thai = Column(Enum(ApartmentStatus), default=ApartmentStatus.CONTRONG)
    image = Column(String(255), nullable=True)
    id_loai_can_ho = Column(Integer, ForeignKey(LoaiCanHo.id), nullable=False)

    def __str__(self):
        return self.ma_can_ho


class HopDong(BaseModel):
    __tablename__ = "hop_dong"

    ngay_ky = Column(DATETIME, nullable=False)
    thoi_han = Column(DATETIME, nullable=False)
    gia_thue = Column(Float, nullable=False)
    tien_coc = Column(Float, nullable=False)

    id_quan_ly = Column(Integer, ForeignKey('admin.user_id'), nullable=False)
    id_nguoi_thue = Column(Integer, ForeignKey('customer.user_id'), nullable=False)
    id_can_ho = Column(Integer, ForeignKey('can_ho.id'), nullable=False)

    def __str__(self):
        return str(self.id)


class DatPhong(BaseModel):
    __tablename__ = "dat_phong"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngay_dat = Column(DATETIME, default=datetime.now())
    ngay_nhan = Column(DATETIME, nullable=False)
    thoi_han = Column(Integer, nullable=False)

    # trạng thái: 0 = chờ duyệt, 1 = đã duyệt
    trang_thai = Column(Integer, default=0)

    customer_id = Column(Integer, ForeignKey('customer.user_id'), nullable=False)
    canho_id = Column(Integer, ForeignKey('can_ho.id'), nullable=False)

    def __str__(self):
        return f"Đơn đặt: {self.id}"


class QuyDinh(BaseModel):
    __tablename__ = "quy_dinh"

    gia_dien = Column(Float, nullable=False, default=0)
    gia_nuoc = Column(Float, nullable=False, default=0)
    so_nguoi_thue_toi_da = Column(Integer, nullable=False, default=4)
    phi_dich_vu = Column(Float, nullable=False, default=0)

    def __str__(self):
        return str(self.id)


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print(">>>Thanh cong")

        import hashlib

        a = Admin(username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), name='Admin',
                  phone=PhoneNumber(phone='0123456789'))
        db.session.add(a)

        t1 = LoaiCanHo(name='1 phòng ngủ')
        t2 = LoaiCanHo(name='2 phòng ngủ')
        t3 = LoaiCanHo(name='3 phòng ngủ')
        t4 = LoaiCanHo(name='4 phòng ngủ')

        if CanHo.query.count() == 0:
            c1 = CanHo(ma_can_ho='P101 - Studio', gia_thue=4500000, dien_tich=30,
                       trang_thai=ApartmentStatus.CONTRONG,
                       image="https://decoxdesign.com/upload/images/thiet-ke-noi-that-chung-cu-70m2-01-decox-design.jpg",
                       id_loai_can_ho=1)
            c2 = CanHo(ma_can_ho='P205 - View Phố', gia_thue=7000000, dien_tich=55,
                       trang_thai=ApartmentStatus.DANGTHUE,
                       image="https://decoxdesign.com/upload/images/thiet-ke-noi-that-chung-cu-70m2-01-decox-design.jpg",
                       id_loai_can_ho=2)
            c3 = CanHo(ma_can_ho='P301 - Full đồ', gia_thue=5500000, dien_tich=40,
                       trang_thai=ApartmentStatus.BAOTRI,
                       id_loai_can_ho=3,
                       image="https://decoxdesign.com/upload/images/thiet-ke-noi-that-chung-cu-70m2-01-decox-design.jpg")
            c4 = CanHo(ma_can_ho='P402 - Penhouse Mini', gia_thue=12000000, dien_tich=80,
                       trang_thai=ApartmentStatus.CONTRONG,
                       id_loai_can_ho=4,
                       image="https://decoxdesign.com/upload/images/thiet-ke-noi-that-chung-cu-70m2-01-decox-design.jpg")
            c5 = CanHo(ma_can_ho='P105 - Gác xép', gia_thue=3500000, dien_tich=25,
                       trang_thai=ApartmentStatus.CONTRONG,
                       id_loai_can_ho=1,
                       image="https://decoxdesign.com/upload/images/thiet-ke-noi-that-chung-cu-70m2-01-decox-design.jpg")

            # Lưu vào session và đẩy xuống DB
            db.session.add_all([t1, t2, t3, t4, c1, c2, c3, c4, c5])

            db.session.commit()

            print(">>> THÀNH CÔNG: Đã tạo bảng và thêm 5 căn hộ mẫu và 1 Admin!")
        else:
            print(">>> THÔNG BÁO: Dữ liệu đã tồn tại, không thêm mới.")

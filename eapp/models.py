from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from __init__ import db, app
from datetime import datetime

import enum

class ApartmentStatus(enum.Enum):
    CONTRONG = 1
    DANGTHUE =2
    BAOTRI = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

class Account(BaseModel):
    __tablename__ = "account"
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)

    #Cột này để phân bệt loại tài khoản (Admin hay Customer)
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
    user_id = Column(Integer, ForeignKey(Account.id),nullable=False)

    def __str__(self):
        return self.phone

class CanHo(BaseModel):
    __tablename__ = "can_ho"

    ma_can_ho = Column(String(50), nullable=False, unique=True)
    gia_thue = Column(Float, default=0)
    dien_tich = Column(Float, default=0)
    trang_thai = Column(Enum(ApartmentStatus), default=ApartmentStatus.CONTRONG)

    def __str__(self):
        return self.ma_can_ho

class HopDong(BaseModel):
    __tablename__ = "hop_dong"

    ngay_ky = Column(DATETIME, nullable=False)
    thoi_han = Column(DATETIME,nullable=False)
    gia_thue = Column(Float, nullable=False)
    tien_coc = Column(Float,nullable=False)

    id_quan_ly = Column(Integer, ForeignKey('admin.user_id'),nullable=False)
    id_nguoi_thue = Column(Integer, ForeignKey('customer.user_id'),nullable=False)
    id_can_ho = Column(Integer, ForeignKey('can_ho.id'), nullable=False)

    def __str__(self):
        return str(self.id)

class QuyDinh(BaseModel):
    __tablename__ = "quy_dinh"

    gia_dien = Column(Float, nullable=False, default=0)
    gia_nuoc = Column(Float, nullable=False, default=0)
    so_nguoi_thue_toi_da = Column(Integer,nullable=False, default=4)
    phi_dich_vu = Column(Float, nullable=False, default=0)

    def __str__(self):
        return str(self.id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(">>>Thanh cong")
        if CanHo.query.count() == 0:
            c1 = CanHo(ma_can_ho='P101 - Studio', gia_thue=4500000, dien_tich=30, trang_thai='CONTRONG')
            c2 = CanHo(ma_can_ho='P205 - 2PN View Phố', gia_thue=7000000, dien_tich=55, trang_thai='DANGTHUE')
            c3 = CanHo(ma_can_ho='P301 - 1PN Full đồ', gia_thue=5500000, dien_tich=40, trang_thai='BAOTRI')
            c4 = CanHo(ma_can_ho='P402 - Penhouse Mini', gia_thue=12000000, dien_tich=80, trang_thai='CONTRONG')
            c5 = CanHo(ma_can_ho='P105 - Gác xép', gia_thue=3500000, dien_tich=25, trang_thai='CONTRONG')

            # Lưu vào session và đẩy xuống DB
            db.session.add_all([c1, c2, c3, c4, c5])
            db.session.commit()

            print(">>> THÀNH CÔNG: Đã tạo bảng và thêm 5 căn hộ mẫu!")
        else:
            print(">>> THÔNG BÁO: Dữ liệu đã tồn tại, không thêm mới.")
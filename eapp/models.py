from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, Float, Boolean

from eapp import db


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

class Account(BaseModel):
    __abstract__ = True
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)

class Admin(Account):
    user_id = Column(Integer, ForeignKey(Account.id), primary_key=True, nullable=False)
    def __str__(self):
        return Admin.name

class Customer(Account):
    user_id = Column(Integer, ForeignKey(Account.id), primary_key=True, nullable=False)
    is_renting = Column(Boolean, default=False)
    def __str__(self):
        return Customer.name

class PhoneNumber(BaseModel):
    phone = Column(String(12), nullable=False, unique=True)
    type = Column(String(50), nullable=False, default='Cell Phone')
    user_id = Column(Integer, ForeignKey(Account.id),nullable=False)
    def __str__(self):
        return self.phone

class HopDong(BaseModel):
    ngay_ky = Column(DATETIME, nullable=False)
    thoi_han = Column(DATETIME,nullable=False)
    gia_thue = Column(Float, nullable=False)
    tien_coc = Column(Float,nullable=False)
    id_quan_ly = Column(Integer, ForeignKey(Admin.id),nullable=False)
    id_nguoi_thue = Column(Integer, ForeignKey(Customer.id),nullable=False)
    id_can_ho = Column(Integer, nullable=False)
    def __str__(self):
        return HopDong.id

class CanHo(BaseModel):
    pass

class QuyDinh(BaseModel):
    gia_dien = Column(Float, nullable=False, default=0)
    gia_nuoc = Column(Float, nullable=False, default=0)
    so_nguoi_thue_toi_da = Column(Integer,nullable=False, default=4)
    phi_dich_vu = Column(Float, nullable=False, default=0)
    def __str__(self):
        return QuyDinh.id
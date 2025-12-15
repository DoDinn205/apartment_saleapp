from tempfile import template

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from __init__ import app, db
from models import CanHo, Account, HopDong, QuyDinh

admin = Admin(app=app, name='QUẢN LÝ CHUNG CƯ')


class CanHoView(ModelView):
    column_list = ('ma_can_ho', 'gia_thue', 'dien_tich', 'trang_thai')
    column_searchable_list = ['ma_can_ho']
    column_filters = ['trang_thai', 'gia_thue']
    column_editable_list = ['trang_thai', 'gia_thue']


class AccountView(ModelView):
    column_list = ('username', 'name', 'user_type')
    column_searchable_list = ['username', 'name']


admin.add_view(CanHoView(CanHo, db.session, name='Căn Hộ'))
admin.add_view(AccountView(Account, db.session, name='Tài Khoản'))
admin.add_view(ModelView(HopDong, db.session, name='Hợp Đồng'))
admin.add_view(ModelView(QuyDinh, db.session, name='Quy Định'))

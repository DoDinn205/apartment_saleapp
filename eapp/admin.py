import cloudinary.uploader
import hashlib
from markupsafe import Markup
from wtforms import FileField
from flask import request
from flask_admin import Admin, BaseView, expose
from flask_admin._types import T_ORM_MODEL
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from wtforms import Form

from __init__ import app, db
from models import CanHo, Account, HopDong, QuyDinh


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


class AccountView(AuthenticatedModelView):
    column_list = ('username', 'name', 'user_type')
    column_searchable_list = ['username', 'name']

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app=app, name='QUẢN LÝ CHUNG CƯ')


class CanHoView(AuthenticatedModelView):
    column_list = ('ma_can_ho', 'gia_thue', 'dien_tich', 'trang_thai', 'image')
    column_searchable_list = ['ma_can_ho']
    column_filters = ['trang_thai', 'gia_thue']
    column_editable_list = ['trang_thai', 'gia_thue']
    can_export = True

    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''
        return Markup('<img src="%s" width="100">' % model.image)

    column_formatters = {
        'image': _list_thumbnail
    }

    form_overrides = {
        'image': FileField
    }

    def on_model_change(self, form, model, is_created):
        if request.files.get('image'):
            try:
                res = cloudinary.uploader.upload(request.files['image'])
                model.image = res['secure_url']
            except Exception as ex:
                print(f"Lỗi upload ảnh: {str(ex)}")


admin.add_view(CanHoView(CanHo, db.session, name='Căn Hộ'))
admin.add_view(AccountView(Account, db.session, name='Tài Khoản'))
admin.add_view(AuthenticatedModelView(HopDong, db.session, name='Hợp Đồng'))
admin.add_view(AuthenticatedModelView(QuyDinh, db.session, name='Quy Định'))

# Thêm nút Đăng xuất
admin.add_view(LogoutView(name='Đăng xuất'))

import cloudinary.uploader
import hashlib
from markupsafe import Markup
from wtforms import FileField
from flask import request, render_template, flash
from flask_admin import Admin, BaseView, expose
from flask_admin._types import T_ORM_MODEL
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from wtforms import Form
from eapp.utils import *
from sqlalchemy.orm import joinedload

from __init__ import app, db
from models import CanHo, Account, HopDong, QuyDinh

@app.route('/admin')
@admin_required  # <--- Gắn cái này vào
def admin_index():
    return render_template('admin/index.html')

# Route quản lý căn hộ
@app.route('/admin/apartments_admin')
@admin_required  # <--- Gắn cái này vào
def apartments_admin():
    selected_type_id = request.args.get('type_id')
    selected_status = request.args.get('status')

    # Logic lấy danh sách căn hộ...
    query = CanHo.query.options(joinedload(CanHo.apartment_type))
    apartment_types = LoaiCanHo.query.all()
    status_list = [
        {'value': 'CONTRONG', 'label': 'Còn trống'},
        {'value': 'DANGTHUE', 'label': 'Đang thuê'},
        {'value': 'BAOTRI', 'label': 'Bảo trì'}
        # Thêm 'DATCOC' nếu có
    ]

    if selected_type_id:
        query = query.filter(CanHo.id_loai_can_ho == int(selected_type_id))

    if selected_status:
        query = query.filter(CanHo.trang_thai == str(selected_status))

    apartments = query.all()



    return render_template('admin/apartments_admin.html',
                           apartments=apartments,
                           apartment_types=apartment_types,
                           status_list=status_list,
                           current_type_id=selected_type_id,
                           current_status=selected_status)


@app.route('/admin/apartments_admin', methods=['POST'])
@admin_required
def update_apartment():
    # 1. Lấy dữ liệu từ form
    apartment_id = request.form.get('id')
    ma_can_ho = request.form.get('ma_can_ho')
    dien_tich = request.form.get('dien_tich')
    gia_thue = request.form.get('gia_thue')
    type_id = request.form.get('type_id')
    status = request.form.get('status')

    # 2. Tìm căn hộ trong DB
    can_ho = CanHo.query.get(apartment_id)

    if can_ho:
        try:
            # 3. Cập nhật thông tin
            can_ho.ma_can_ho = ma_can_ho
            can_ho.dien_tich = float(dien_tich)
            can_ho.gia_thue = float(gia_thue)
            can_ho.id_loai_can_ho = int(type_id)
            can_ho.trang_thai = status  # SQLAlchemy tự map chuỗi sang Enum nếu khớp tên

            # 4. Lưu vào DB
            db.session.commit()
            flash('Cập nhật thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi cập nhật: {str(e)}', 'danger')
    else:
        flash('Không tìm thấy căn hộ!', 'danger')

    # 5. Quay lại trang danh sách (giữ lại các tham số lọc nếu muốn - phần nâng cao)
    return redirect(url_for('apartments_admin'))
admin = Admin(app=app, name='QUẢN LÝ CHUNG CƯ')


#T comment đoạn code trở về sau vì mình đã tự tạo trang admin riêng rồi nên không cần thiết dùng mấy cái view mặc định nữa

# class AuthenticatedModelView(ModelView):
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_type == 'admin'
#
#     def inaccessible_callback(self, name, **kwargs):
#         return redirect('/login')
#
#
# class AuthenticatedBaseView(BaseView):
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_type == 'admin'
#
#     def inaccessible_callback(self, name, **kwargs):
#         return redirect('/login')


# class AccountView(AuthenticatedModelView):
#     column_list = ('username', 'name', 'user_type')
#     column_searchable_list = ['username', 'name']
#
#     def on_model_change(self, form, model, is_created):
#         if form.password.data:
#             model.password = str(hashlib.md5(form.password.data.encode('utf-8')).hexdigest())


# class LogoutView(BaseView):
#     @expose('/')
#     def index(self):
#         logout_user()
#         return redirect('/admin')
#
#     def is_accessible(self):
#         return current_user.is_authenticated








# class CanHoView(AuthenticatedModelView):
#     column_list = ('ma_can_ho', 'gia_thue', 'dien_tich', 'trang_thai', 'image')
#     column_searchable_list = ['ma_can_ho']
#     column_filters = ['trang_thai', 'gia_thue']
#     column_editable_list = ['trang_thai', 'gia_thue']
#     can_export = True
#
#     def _list_thumbnail(view, context, model, name):
#         if not model.image:
#             return ''
#         return Markup('<img src="%s" width="100">' % model.image)
#
#     column_formatters = {
#         'image': _list_thumbnail
#     }
#
#     form_overrides = {
#         'image': FileField
#     }
#
#     def on_model_change(self, form, model, is_created):
#         if request.files.get('image'):
#             try:
#                 res = cloudinary.uploader.upload(request.files['image'])
#                 model.image = res['secure_url']
#             except Exception as ex:
#                 print(f"Lỗi upload ảnh: {str(ex)}")
#
#
# admin.add_view(CanHoView(CanHo, db.session, name='Căn Hộ'))
# admin.add_view(AccountView(Account, db.session, name='Tài Khoản'))
# admin.add_view(AuthenticatedModelView(HopDong, db.session, name='Hợp Đồng'))
# admin.add_view(AuthenticatedModelView(QuyDinh, db.session, name='Quy Định'))

# Thêm nút Đăng xuất
# admin.add_view(LogoutView(name='Đăng xuất'))

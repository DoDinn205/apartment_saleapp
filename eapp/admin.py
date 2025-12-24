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
from utils import *
from sqlalchemy.orm import joinedload
from models import HoaDon
from __init__ import app, db

from models import QuyDinh, Account, Customer, HopDong, CanHo, ApartmentStatus, PhoneNumber, ChiTietHopDong


@app.route('/admin')
@admin_required
def admin_index():
    return render_template('admin/index.html')


# Route quản lý căn hộ
@app.route('/admin/apartments_admin')
@admin_required
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


@app.route('/admin/regulations')
@admin_required
def regulations_admin():
    print(">>> ĐANG CHẠY HÀM REGULATIONS_ADMIN...")
    qd = QuyDinh.query.first()
    if qd:
        print(f">>> CÓ DỮ LIỆU TRONG DB! ID={qd.id}")
        print(f">>> Giá điện: {qd.gia_dien}, Giá nước: {qd.gia_nuoc}")
    else:
        print(">>> KHÔNG TÌM THẤY DỮ LIỆU (qd is None)")
        # Tự động tạo nếu không có
        qd = QuyDinh(gia_dien=3500, gia_nuoc=20000, phi_dich_vu=150000, so_nguoi_thue_toi_da=4)
        db.session.add(qd)
        db.session.commit()
        print(">>> ĐÃ TẠO MỚI DỮ LIỆU THÀNH CÔNG!")
    # if not qd:
    #     return render_template('admin/regulations_admin.html', regulations=[])
    #     # qd = QuyDinh(gia_dien=3500, gia_nuoc=20000, so_nguoi_thue_toi_da=4, phi_dich_vu=150000)
    #     # db.session.add(qd)
    #     # db.session.commit()
    #     # print("Đã khởi tạo dữ liệu Quy định mặc định!")

    regulations_list = [
        {'key': 'gia_dien', 'name': 'Đơn giá Điện (vnđ/kWh)', 'value': qd.gia_dien},
        {'key': 'gia_nuoc', 'name': 'Đơn giá Nước (vnđ/m3)', 'value': qd.gia_nuoc},
        {'key': 'so_nguoi_thue_toi_da', 'name': 'Số người thuê tối đa / phòng', 'value': qd.so_nguoi_thue_toi_da},
        {'key': 'phi_dich_vu', 'name': 'Phí Dịch vụ (vnđ/tháng)', 'value': qd.phi_dich_vu}
    ]

    print(f">>> LIST TRẢ VỀ HTML CÓ {len(regulations_list)} DÒNG.")

    return render_template('admin/regulations_admin.html', regulations_list=regulations_list)


@app.route('/admin/regulations/update', methods=['POST'])
@admin_required
def update_regulation():
    column_name = request.form.get('id')
    new_value = request.form.get('value')

    if column_name and new_value:
        try:
            qd = QuyDinh.query.first()
            if qd and hasattr(qd, column_name):
                setattr(qd, column_name, float(new_value))
                db.session.commit()
                print("Cập nhật thành công!")
        except Exception as e:
            print(f"Lỗi cập nhật: {e}")

    return redirect(url_for('regulations_admin'))


@app.route('/admin/contracts')
@admin_required
def contracts_admin():
    contracts = HopDong.query.options(
        joinedload(HopDong.khach_hang),
        joinedload(HopDong.can_ho)
    ).order_by(HopDong.ngay_ky.desc()).all()

    customers = Customer.query.all()

    # Lấy danh sách phòng TRỐNG để chọn
    empty_apartments = CanHo.query.filter_by(trang_thai=ApartmentStatus.CONTRONG).all()

    return render_template('admin/contracts_admin.html',
                           contracts=contracts,
                           customers=customers,
                           empty_apartments=empty_apartments,
                           now_date=datetime.now().strftime('%Y-%m-%d'))


@app.route('/admin/contracts/create', methods=['POST'])
@admin_required
def create_contract():
    # --- 1. LẤY DỮ LIỆU TỪ FORM ---
    ma_can_ho_str = request.form.get('ma_can_ho')  # Đây là Mã hiển thị (VD: P101)

    # Xử lý ngày tháng (HTML date input trả về chuỗi YYYY-MM-DD)
    try:
        ngay_ky = datetime.strptime(request.form.get('ngay_ky'), '%Y-%m-%d')
        ngay_tra = datetime.strptime(request.form.get('ngay_tra'), '%Y-%m-%d')
        tien_coc = float(request.form.get('tien_coc'))
        gia_chot_thue = float(request.form.get('gia_chot_thue'))
    except ValueError:
        return redirect(url_for('contract_list'))



    # --- 2. XỬ LÝ NGƯỜI THUÊ ---
    option = request.form.get('customer_option')
    customer_obj = None

    try:
        if option == 'existing':
            cus_id_input = request.form.get('customer_id')
            customer_obj = Customer.query.get(cus_id_input)

            if not customer_obj:
                return redirect(url_for('contract_list'))

        elif option == 'new':
            name = request.form.get('new_name')
            phone_str = request.form.get('new_phone')

            # Kiểm tra trùng Username (Username là SĐT)
            if Account.query.filter_by(username=phone_str).first():
                flash(f'Tài khoản/SĐT {phone_str} đã tồn tại trong hệ thống!', 'danger')
                return redirect(url_for('contract_list'))

            # Kiểm tra trùng trong bảng PhoneNumber (cho chắc chắn)
            if PhoneNumber.query.filter_by(phone=phone_str).first():
                flash(f'Số điện thoại {phone_str} đã được liên kết với tài khoản khác!', 'danger')
                return redirect(url_for('contract_list'))

            # Tạo Customer Mới (Account)
            default_pass = hashlib.md5("123456".encode('utf-8')).hexdigest()
            new_customer = Customer(
                username=phone_str,  # Username = SĐT
                password=default_pass,
                name=name,
                user_type='customer',
                is_renting=True,  # Đánh dấu là đang thuê
            )

            db.session.add(new_customer)
            db.session.flush()  # Đẩy tạm vào DB để sinh ra new_customer.id (Integer)

            # Tạo PhoneNumber Mới (Liên kết với Customer vừa tạo)
            new_phone = PhoneNumber(
                phone=phone_str,
                user_id=new_customer.id  # Lấy ID vừa flush
            )
            db.session.add(new_phone)

            # Gán đối tượng vừa tạo vào biến chung
            customer_obj = new_customer

            flash(f'Đã tạo tài khoản mới cho {name}. Mật khẩu: 123456', 'info')

        # --- 3. TẠO HỢP ĐỒNG ---
        # Tìm đối tượng Căn hộ dựa trên Mã căn hộ (String)
        room_obj = CanHo.query.filter_by(ma_can_ho=ma_can_ho_str).first()
        current_rule = QuyDinh.query.order_by(QuyDinh.id.desc()).first()

        # Khởi tạo Hợp đồng
        new_hd = HopDong(
            ngay_ky=ngay_ky,
            ngay_tra=ngay_tra,
            tien_coc=tien_coc,
            gia_chot_thue=gia_chot_thue,
            id_quan_ly=current_user.id,
            id_nguoi_thue=customer_obj.id,
            id_can_ho=room_obj.id,
            id_quy_dinh=current_rule.id
        )

        # --- 4. CẬP NHẬT TRẠNG THÁI ---
        # Cập nhật trạng thái phòng -> Đã thuê
        room_obj.trang_thai = ApartmentStatus.DANGTHUE
        # Cập nhật trạng thái người dùng (nếu chọn người cũ chưa thuê)
        customer_obj.is_renting = True

        db.session.add(new_hd)
        db.session.flush()

        new_detail = ChiTietHopDong(
            id_hop_dong=new_hd.id,
            id_nguoi_thue=customer_obj.id
        )
        db.session.add(new_detail)

        db.session.commit()

        flash('Tạo hợp đồng thành công!', 'success')

    except Exception as e:
        db.session.rollback()  # Hoàn tác nếu có lỗi
        print(f"Error: {str(e)}")  # In lỗi ra console để debug
        flash(f'Đã xảy ra lỗi: {str(e)}', 'danger')

    return redirect(url_for('contracts_admin'))

@app.route('/admin/contracts/add-member', methods=['POST'])
@admin_required
def add_contract_member():
    contract_id = request.form.get('contract_id')
    customer_id = request.form.get('customer_id') # ID của người được chọn thêm vào

    contract = HopDong.query.get(contract_id)
    customer = Customer.query.get(customer_id)

    if not contract or not customer:
        flash('Dữ liệu không hợp lệ', 'danger')
        return redirect(url_for('contracts_admin'))

    # 1. Kiểm tra quy định tối đa 4 người
    # Đếm số record trong bảng ChiTietHopDong của hợp đồng này
    current_members = ChiTietHopDong.query.filter_by(id_hop_dong=contract_id).count()
    if current_members >= 4:
        flash('Hợp đồng này đã đủ 4 người. Không thể thêm!', 'warning')
        return redirect(url_for('contracts_admin'))

    # 2. Kiểm tra xem người này đã có trong hợp đồng chưa
    exists = ChiTietHopDong.query.filter_by(id_hop_dong=contract_id, id_nguoi_thue=customer_id).first()
    if exists:
        flash('Người này đã có trong danh sách cư dân!', 'warning')
        return redirect(url_for('contracts_admin'))

    # 3. Thêm vào bảng chi tiết
    try:
        new_member = ChiTietHopDong(
            id_hop_dong=contract_id,
            id_nguoi_thue=customer_id,
            vai_tro='Thành viên'
        )
        customer.is_renting = True # Cập nhật trạng thái khách
        db.session.add(new_member)
        db.session.commit()
        flash(f'Đã thêm {customer.name} vào căn hộ!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {str(e)}', 'danger')

    return redirect(url_for('contracts_admin'))


@app.route('/admin/contracts/extend', methods=['POST'])
@admin_required
def extend_contract():
    ma_hd = request.form.get('ma_hop_dong')
    new_date_str = request.form.get('new_date')
    contract = HopDong.query.get(ma_hd)
    if contract and new_date_str:
        # Chuyển string sang datetime
        contract.ngay_tra = datetime.strptime(new_date_str, '%Y-%m-%d')
        db.session.commit()
        flash('Gia hạn thành công!', 'success')
    else:
        flash('Lỗi khi gia hạn!', 'danger')

    return redirect(url_for('contracts_admin'))


@app.route('/admin/contracts/cancel', methods=['POST'])
@admin_required
def cancel_contract():
    ma_hd = request.form.get('ma_hop_dong')
    contract = HopDong.query.get(ma_hd)

    if contract:
        db.session.delete(contract)

        db.session.commit()
        flash('Đã hủy hợp đồng thành công!', 'success')

    return redirect(url_for('contracts_admin'))


@app.route('/admin/tenants')
@admin_required
def tenant_manager():
    tenants_data = db.session.query(
        HopDong.id,
        Customer.name,
        Customer.avatar,
        PhoneNumber.phone,
        CanHo.ma_can_ho,
        HopDong.ngay_ky,
        HopDong.ngay_tra,
        HopDong.tien_coc
    ).join(Customer, HopDong.id_nguoi_thue == Customer.user_id) \
        .join(CanHo, HopDong.id_can_ho == CanHo.id) \
        .outerjoin(PhoneNumber, Account.id == PhoneNumber.user_id) \
        .all()

    return render_template('admin/tenant_manager.html', tenants=tenants_data)


class HoaDonView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == 'admin'

    column_labels = {
        'ten_hoa_don': 'Nội dung',
        'so_tien': 'Số tiền (vnđ)',
        'ngay_tao': 'Ngày tạo',
        'trang_thai': 'Trạng thái',
        'hop_dong': 'Hợp đồng',
        'test_payment': 'Thanh toán'
    }

    column_list = ['id', 'ten_hoa_don', 'so_tien', 'trang_thai', 'test_payment']

    def _test_payment_link(view, context, model, name):
        if not model.trang_thai:
            checkout_url = f"/payment/checkout/{model.id}"
            return Markup(
                f'<a href="{checkout_url}" target="_blank" class="btn btn-sm btn-warning">Thanh toán tại đây</a>')
        return Markup('<span class="badge bg-success">Đã thanh toán</span>')

    column_formatters = {
        'so_tien': lambda v, c, m, p: "{:,.0f}".format(m.so_tien),
        'test_payment': _test_payment_link
    }

    form_columns = ['ten_hoa_don', 'so_tien', 'trang_thai', 'hop_dong']


admin.add_view(HoaDonView(HoaDon, db.session, name='Quản lý Hóa đơn', endpoint='hoadon'))

# T comment đoạn code trở về sau vì mình đã tự tạo trang admin riêng rồi nên không cần thiết dùng mấy cái view mặc định nữa

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

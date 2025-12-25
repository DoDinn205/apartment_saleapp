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
from dateutil.relativedelta import relativedelta

from models import QuyDinh, Account, Customer, HopDong, CanHo, ApartmentStatus, PhoneNumber, ChiTietHopDong


@app.route('/admin')
@admin_required
def admin_index():
    return render_template('admin/index.html')


@app.route('/index')
@admin_required
def return_client_view():
    return redirect('/')


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

    customers = get_not_renting_customers()

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
    try:
        contract_data = {
            'ma_can_ho': request.form.get('ma_can_ho'),
            'ngay_ky': datetime.strptime(request.form.get('ngay_ky'), '%Y-%m-%d'),
            'ngay_tra': datetime.strptime(request.form.get('ngay_tra'), '%Y-%m-%d'),
            'tien_coc': float(request.form.get('tien_coc')),
            'gia_chot_thue': float(request.form.get('gia_chot_thue'))
        }
    except ValueError:
        flash('Dữ liệu ngày tháng hoặc tiền tệ không hợp lệ.', 'danger')
        return redirect(url_for('contracts_admin'))

    option = request.form.get('customer_option')

    customer_obj = handle_customer_selection(option, request.form)
    if not customer_obj:
        flash("Không lấy được thông tin người dùng", 'danger')
        return redirect(url_for('contracts_admin'))

    is_success = process_create_contract(
        contract_data=contract_data,
        customer_obj=customer_obj,
        manager_id=current_user.id
    )
    if is_success:
        flash("Tạo thành công", 'success')
    else:
        flash("Tạo thất bại", 'danger')

    return redirect(url_for('contracts_admin'))


@app.route('/admin/contracts/add-member', methods=['POST'])
@admin_required
def add_contract_member():
    contract_id = request.form.get('contract_id')
    customer_id = request.form.get('customer_id')  # ID của người được chọn thêm vào

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
        customer.is_renting = True  # Cập nhật trạng thái khách
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
        u = Customer.query.get(contract.id_nguoi_thue)
        u.is_renting = False

        db.session.delete(contract)

        db.session.commit()
        flash('Đã hủy hợp đồng thành công!', 'success')

    return redirect(url_for('contracts_admin'))


@app.route('/admin/tenants')
@admin_required
def tenant_manager():
    # tenants_data = db.session.query(
    #     HopDong.id,
    #     Customer.name,
    #     Customer.avatar,
    #     PhoneNumber.phone,
    #     CanHo.ma_can_ho,
    #     HopDong.ngay_ky,
    #     HopDong.ngay_tra,
    #     HopDong.tien_coc
    # ).join(Customer, HopDong.id_nguoi_thue == Customer.user_id) \
    #     .join(CanHo, HopDong.id_can_ho == CanHo.id) \
    #     .outerjoin(PhoneNumber, Account.id == PhoneNumber.user_id) \
    #     .all()
    tenants_data = HopDong.query.options(
        joinedload(HopDong.khach_hang).joinedload(Customer.phone),  # Nối bảng khách và sđt
        joinedload(HopDong.can_ho)  # Nối bảng căn hộ
    ).all()

    return render_template('admin/tenant_manager.html', tenants=tenants_data)


@app.route('/admin/tenant/update', methods=['POST'])
def update_tenant_info():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    phone_number = request.form.get('phone')

    customer = Customer.query.get(user_id)
    if customer:
        customer.name = name

        if customer.phone:
            customer.phone.phone = phone_number
        else:
            new_phone = PhoneNumber(phone=phone_number, user_id=customer.id)
            db.session.add(new_phone)

        db.session.commit()
        flash('Cập nhật thông tin khách hàng thành công!', 'success')

    return redirect('/admin/tenants')


@app.route('/admin/notifications')
@admin_required
def admin_booking():
    bookings = DatPhong.query.filter_by(trang_thai=0).all()
    return render_template('admin/notification_admin.html', bookings=bookings)


@app.route('/admin/booking/approve<id>')
@admin_required
def approve_booking(id):
    booking = DatPhong.query.get(id)
    existing_contract = HopDong.query.filter_by(
        id_nguoi_thue=booking.customer.id
    ).first()

    if existing_contract is None:
        return redirect(url_for('contracts_admin'))

    booking.trang_thai=1
    db.session.add(booking)

    noti = Notification(
        sender_id=current_user.id,
        receiver_id=booking.customer.id,
        booking_id=booking.id,
        title='Đặt phòng thành công',
        content='Yêu cầu thuê phòng ' + booking.can_ho.ma_can_ho + ' của bạn đã được duyệt'
    )
    db.session.add(noti)
    db.session.commit()

    return redirect('/admin/notifications')


@app.route('/admin/booking/reject<id>')
@admin_required
def reject_booking(id):
    booking = DatPhong.query.get(id)
    booking.trang_thai = 2

    db.session.add(booking)

    noti = Notification(
        sender_id=current_user.id,
        receiver_id=booking.customer.id,
        booking_id=booking.id,
        title='Đặt phòng thất bại',
        content='Yêu cầu thuê phòng ' + booking.can_ho.ma_can_ho + ' của bạn đã bị quản lý từ chối'
    )
    db.session.add(noti)
    db.session.commit()

    return redirect('/admin/notifications')

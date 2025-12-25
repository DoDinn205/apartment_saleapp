from flask import render_template, request, redirect, url_for, flash, jsonify
from __init__ import app, login
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql.operators import endswith_op
from models import HoaDon, HopDong, db
import math
import os
import utils
from admin import *
from forms import RegisterForm, AvatarForm
from utils import check_login


@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    ds_canho = utils.load_canho(kw=request.args.get('keyword'),
                                loai_canho_id=request.args.get('id_loai_can_ho'),
                                page=page)

    return render_template('index.html', apartments=ds_canho, page=page,
                           pages=math.ceil(utils.count_apartment() / app.config['PAGE_SIZE']))


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id)


# ---Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login_view():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = utils.check_login(username=username, password=password)

        if user:
            login_user(user=user)

            if user.user_type == 'admin':
                return redirect('/admin')
            else:
                return redirect('/')

        else:
            err_msg = 'Sai tên đăng nhập hoặc mật khẩu!'

    return render_template('login.html', err_msg=err_msg)


# ---Đăng ký
@app.route('/register', methods=['get', 'post'])
def register_view():
    form = RegisterForm()
    err_msg = None
    if form.validate_on_submit():
        try:
            utils.add_user(
                name=form.name.data,
                phone=form.phone.data,
                username=form.username.data,
                password=form.password.data,
                avatar=form.avatar.data
            )
            return redirect('/login')
        except Exception as ex:
            err_msg = str(ex)

    return render_template('register.html', form=form, err_msg=err_msg)


# ---Thông tin tài khoản
@app.route('/info_account', methods=['get', 'post'])
@login_required
def info_account_view():
    form = AvatarForm()
    if form.validate_on_submit() and form.avatar.data:
        try:
            res = cloudinary.uploader.upload(
                form.avatar.data,
                overwrite=True
            )

            current_user.avatar = res.get('secure_url')
            db.session.commit()

        except Exception as ex:
            print("Lỗi upload avatar:", str(ex))

        return redirect('/info_account')

    return render_template('info_account.html', form=form)


@app.route('/admin/index')
@admin_required
def admin_view():
    return render_template('/admin/index.html')


# ---Đăng xuất
@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/')


# ---Chi tiết căn hộ
@app.route('/apartments/<int:apartment_id>')
def apartment_detail(apartment_id):
    phong = utils.get_canho_by_id(apartment_id)
    return render_template('apartment.html', apartment=phong)


# ---Đặt phòng
@app.route('/booking', methods=['POST'])
@login_required
def booking_process():
    if current_user.is_renting != True:

        try:
            canho_id = request.form.get('apartment_id')
            ngay_nhan = request.form.get('start_date')
            thoi_han = request.form.get('duration')
            tien_coc = request.form.get('tien_coc')
            ds_canho = utils.load_canho(canho_id)
            page = 1

            if utils.add_booking(current_user.id, canho_id, ngay_nhan, thoi_han, tien_coc):
                msg = 'Bạn đã đặt phòng thành công. Chúng tôi sẽ liên hệ bạn sớm!'
                return render_template('index.html', apartments=ds_canho, success_msg=msg, page=page,
                                       pages=math.ceil(utils.count_apartment() / app.config['PAGE_SIZE']))
            else:
                err = 'Có lỗi xảy ra. Vui lòng thử lại sau!'
                return render_template('index.html', apartments=ds_canho, err_msg=err, page=page,
                                       pages=math.ceil(utils.count_apartment() / app.config['PAGE_SIZE']))
        except Exception as ex:
            return render_template('index.html', apartments=ds_canho, err_msg=f'Lỗi hệ thống: {str(ex)}', page=page,
                                   pages=math.ceil(utils.count_apartment() / app.config['PAGE_SIZE']))
    else:
        return render_template('index.html')


@app.route('/api/notifications')
@login_required
def notifications():
    notis = Notification.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Notification.ngay_tao.desc()).all()

    return jsonify([
        {
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'ngay_tao': n.ngay_tao
        }
        for n in notis
    ])


@app.context_processor
def common_response():
    image = []
    try:
        img_folder = os.path.join(app.static_folder, 'images/banner')
        if os.path.exists(img_folder):
            images = [
                'images/banner/' + img for img in os.listdir(img_folder)
                if img.lower().endswith(('.jpg', '.png', '.jpeg', '.gif'))
            ]
    except Exception as e:
        print(f"Lỗi load banner: {e}")
    return {
        'loai_canho': utils.load_loai_canho(),
        'images': images
    }


# Thanh toán
@app.route('/payment/checkout/<int:bill_id>')
def payment_ui(bill_id):
    hoa_don = HoaDon.query.get(bill_id)

    if not hoa_don:
        return "Hóa đơn không tồn tại", 404

    if hoa_don.trang_thai:
        return "Hóa đơn này đã được thanh toán rồi!"

    return render_template('payment/fake_momo.html', bill=hoa_don)


# 2. Route xử lý khi bấm nút "Xác nhận đã thanh toán"
@app.route('/payment/confirm/<int:bill_id>', methods=['POST'])
def payment_confirm(bill_id):
    hoa_don = HoaDon.query.get(bill_id)

    if hoa_don:
        hoa_don.trang_thai = True
        db.session.commit()
        flash('Thanh toán thành công!', 'success')

    return redirect(url_for('invoice_manager'))


# Danh sách Hóa đơn
@app.route('/admin/invoice-manager')
def invoice_manager():
    ds_hoa_don = HoaDon.query.order_by(HoaDon.id.desc()).all()
    ds_hop_dong = HopDong.query.all()
    return render_template('admin/invoice_manager.html',
                           invoices=ds_hoa_don,
                           contracts=ds_hop_dong)


# Thêm Hóa đơn mới
@app.route('/admin/invoice/add', methods=['POST'])
def add_invoice():
    ten_hoa_don = request.form.get('ten_hoa_don')
    so_tien = request.form.get('so_tien')
    hop_dong_id = request.form.get('hop_dong_id')

    new_bill = HoaDon(
        ten_hoa_don=ten_hoa_don,
        so_tien=float(so_tien),
        id_hop_dong=hop_dong_id,
        trang_thai=False
    )

    db.session.add(new_bill)
    db.session.commit()
    flash('Đã tạo hóa đơn thành công!', 'success')
    return redirect(url_for('invoice_manager'))


# Sửa Hóa đơn
@app.route('/admin/invoice/update', methods=['POST'])
def update_invoice():
    invoice_id = request.form.get('id')
    ten_hoa_don = request.form.get('ten_hoa_don')
    so_tien = request.form.get('so_tien')
    hop_dong_id = request.form.get('hop_dong_id')
    trang_thai = request.form.get('trang_thai')

    hoa_don = HoaDon.query.get(invoice_id)

    if hoa_don:
        hoa_don.ten_hoa_don = ten_hoa_don
        hoa_don.so_tien = float(so_tien)
        hoa_don.id_hop_dong = hop_dong_id

        hoa_don.trang_thai = True if trang_thai == 'on' else False

        db.session.commit()
        flash('Cập nhật hóa đơn thành công!', 'success')

    return redirect(url_for('invoice_manager'))


# Xóa Hóa đơn
@app.route('/admin/invoice/delete/<int:id>')
def delete_invoice(id):
    hoa_don = HoaDon.query.get(id)
    if hoa_don:
        db.session.delete(hoa_don)
        db.session.commit()
        flash('Đã xóa hóa đơn!', 'success')
    return redirect(url_for('invoice_manager'))


if __name__ == '__main__':
    app.run(debug=True)

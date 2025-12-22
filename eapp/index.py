from flask import render_template, request, redirect, url_for
from __init__ import app, login
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql.operators import endswith_op

import math
import os
import utils
from admin import *
from forms import RegisterForm, AvatarForm
from utils import check_login


@app.route('/')
def index():
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

    loai_canho = utils.load_loai_canho()

    page = int(request.args.get('page', 1))
    ds_canho = utils.load_canho(kw=request.args.get('keyword'),
                                loai_canho_id=request.args.get('id_loai_can_ho'),
                                page=page)

    return render_template('index.html', images=images, apartments=ds_canho, page=page,
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
    try:
        canho_id = request.form.get('apartment_id')
        ngay_nhan = request.form.get('start_date')
        thoi_han = request.form.get('duration')

        if utils.add_booking(current_user.id, canho_id, ngay_nhan, thoi_han):
            ds_canho = utils.load_canho(canho_id)
            msg = 'Bạn đã đặt phòng thành công. Chúng tôi sẽ liên hệ bạn sớm!'
            return render_template('index.html', apartments=ds_canho, success_msg=msg)
        else:
            ds_canho = utils.load_canho(canho_id)
            err = 'Có lỗi xảy ra. Vui lòng thử lại sau!'
            return render_template('index.html', apartments=ds_canho, err_msg=err)
    except Exception as ex:
        ds_canho = utils.load_canho(canho_id)
        return render_template('index.html', apartments=ds_canho, err_msg=f'Lỗi hệ thống: {str(ex)}')


@app.context_processor
def common_response():
    return {
        'loai_canho': utils.load_loai_canho()
    }


if __name__ == '__main__':
    app.run(debug=True)

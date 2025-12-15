from flask import render_template, request
from __init__ import app
from sqlalchemy.sql.operators import endswith_op


import os
import utils
from admin import *


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

    room_types=[
        {
            'id': 1,
            'name': '1 phòng ngủ'
        },
        {
            'id': 2,
            'name': '2 phòng ngủ'
        },
        {
            'id': 3,
            'name': '3 phòng ngủ'
        },
        {
            'id': 4,
            'name': '4 phòng ngủ'
        }
    ]

    kw=request.args.get('keyword')

    ds_canho=utils.load_canho(kw=kw)

    return render_template('index.html', images=images, room_types=room_types, apartments=ds_canho)

#---Đăng nhập
@app.route('/login')
def login_view():
    return render_template('login.html')

#---Đăng ký
@app.route('/register')
def register_view():
    return render_template('register.html')

#---Chi tiết căn hộ
@app.route('/apartments/<int:apartment_id>')
def apartment_detail(apartment_id):
    phong=utils.get_canho_by_id(apartment_id)
    return render_template('apartment.html', apartment=phong)

if __name__ == '__main__':
    app.run(debug=True)

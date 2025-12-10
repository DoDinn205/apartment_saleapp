from flask import render_template
from sqlalchemy.sql.operators import endswith_op

from eapp import app
import os


@app.route('/')
def index():
    img_folder = os.path.join(app.static_folder, 'images/banner')
    images = [
        'images/banner/' + img for img in os.listdir(img_folder)
        if img.lower().endswith(('.jpg', '.png', '.jpeg', '.gif'))
    ]

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
    return render_template('index.html', images=images, room_types=room_types)


@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/register')
def register_view():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)

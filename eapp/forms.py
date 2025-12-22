from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    name = StringField(
        'Họ tên',
        validators=[DataRequired(message='Vui lòng nhập họ tên')]
    )
    phone = StringField(
        'Số điện thoại',
        validators=[DataRequired(message='Vui lòng nhập số điện thoại'), Length(min=10, max=10)]
    )
    username = StringField(
        'Tên đăng nhập',
        validators=[DataRequired(message='Vui lòng nhập tên đăng nhập'), Length(min=6)]
    )

    password = PasswordField(
        'Mật khẩu',
        validators=[DataRequired(message='Vui lòng nhập mật khẩu'), Length(min=6)]
    )

    confirm = PasswordField(
        'Nhập lại mật khẩu',
        validators=[DataRequired(), EqualTo('password', message='Mật khẩu không khớp')]
    )

    avatar = FileField(
        'Avatar',
        validators=[
            FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ cho phép ảnh!')
        ]
    )

    submit = SubmitField('Đăng ký')

class AvatarForm(FlaskForm):
    avatar = FileField(
        'Avatar',
        validators=[
            FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ cho phép ảnh!')
        ]
    )

    submit = SubmitField('Cập nhật')

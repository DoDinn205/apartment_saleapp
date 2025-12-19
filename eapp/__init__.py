from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = 'BiMat123'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:tatvanlong123@localhost/apartmentdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app=app)

login = LoginManager(app=app)

cloudinary.config(
    cloud_name="dzlfmtf2q",
    api_key="394863965996431",
    api_secret="3ZOOFpQffZyxR2gmN_3e_zDSrnM"
)

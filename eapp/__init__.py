from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = 'BiMat123'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345678@localhost/apartmentdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE']=6
db = SQLAlchemy(app=app)

login = LoginManager(app=app)

cloudinary.config(
    cloud_name="dyjdromdd",
    api_key="637151337155997",
    api_secret="Ypv7wLEEZSdtey5II_Rv1DJXsm0"
)

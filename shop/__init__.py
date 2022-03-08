from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from datetime import timedelta
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
mail = Mail(app)
app.secret_key = "L31 CHU X1@"
app.permanent_session_lifetime = timedelta(hours=1)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Project_Shop'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'official.aboveaverage21@gmail.com'
app.config['MAIL_PASSWORD'] = '@b0v3@v3r@g3'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

otp = None
mail = Mail(app)
mysql = MySQL(app)
bcrypt = Bcrypt(app)

from shop.admin import routes
from shop.products import routes
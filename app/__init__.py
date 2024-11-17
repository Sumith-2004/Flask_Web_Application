from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = '41d90f1f1a9e1003e6977eea3d93e83f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.permanent_session_lifetime = timedelta(days=1)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


from app import models, forms, routes
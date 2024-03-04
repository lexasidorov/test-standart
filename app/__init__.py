from app.config import SECRET_KEY, SQLALCHEMY_DATABASE_URI
from flask import Flask
from sqlalchemy import create_engine
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db.init_app(app)
migrate.init_app(app, db)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

from app import models, routes
models.Base.metadata.create_all(bind=engine)

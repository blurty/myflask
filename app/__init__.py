from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from .config.config import config
from flask_pagedown import PageDown

bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()
moment = Moment()
login_manager.session_protection = 'strong'
db = SQLAlchemy()
pagedown = PageDown()


# create app
def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config[config_name])

    import logging
    from logging.handlers import RotatingFileHandler
    _handler = RotatingFileHandler(app.config['LOGGER_NAME'], maxBytes=10000, backupCount=1)
    _handler.setLevel(logging.DEBUG)
    app.logger.addHandler(_handler)

    pagedown.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    app.secret_key = app.config['SECRET_KEY']
    app.permanent_session_lifetime = timedelta(minutes=5)

    login_manager.init_app(app)
    db.init_app(app)
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api')
    from .base import base
    app.register_blueprint(base)
    from .rest_api import rest_api
    app.register_blueprint(rest_api, url_prefix='/rest')

    from .models import Role
    @app.before_first_request
    def build_up_before_start():
        Role.insert_roles()
    return app

# create db
from .sqllib import DataBaseClient
def create_db():
    sql = "create table user_info ( \
    `id` int not null, \
    `username` varchar(20) not null unique, \
    `passwd` varchar(10) not null, \
    `role` int not null, \
    primary key (`id`))"
    db = DataBaseClient(path='data-base.db')
    ret = db.execute(sql)
    if not ret:
        return 0    # failed
    return 1


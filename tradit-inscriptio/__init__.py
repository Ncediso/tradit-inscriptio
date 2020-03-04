# -*- coding: utf-8 -*-
"""Main application package."""

# init.py

from flask import Flask, render_template, session
import smtplib
# import
import sqlalchemy as sa

# engine = sa.create_engine('mssql+pyodbc://user:password@server/database')
from flask import Flask, render_template, session
# from flask_sqlalchemy import SQLAlchemy
# from .app_utils .logging_config import *
from datetime import datetime, timedelta
# from flask_mail import Mail

app = Flask(__name__)


def _register_blueprints():
    """"""
    # blueprint for non-auth parts of app
    from .endpoints.main import main as main_blueprint
    app.register_blueprint(main_blueprint)


_register_blueprints()


# -*- coding: utf-8 -*-
"""Main application package."""

import os
import logging
from config import Config
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from .app_utils.logging_config import ContextualFilter, get_file_logger_handler, get_stream_logger_handler


LOGGER = logging.getLogger(__name__)
db = SQLAlchemy()


def _register_blueprints(main_app):
    """

    :param main_app:
    :return:
    """

    from .endpoints.main import main as main_blueprint
    main_app.register_blueprint(main_blueprint)

    from .endpoints.tables import tables as tables_blueprint
    main_app.register_blueprint(tables_blueprint)
    # main_app.logger.info("End points registered successfully.")
    return main_app


def _register_login_handlers(main_app):
    """

    :param main_app: FLask Application
    :return:
    """

    context_provider = ContextualFilter()
    main_app.logger.addFilter(context_provider)

    stream_handler = get_stream_logger_handler()
    main_app.logger.addHandler(stream_handler)

    # mail_handler = get_smtp_logger_handler()
    # app.logger.addHandler(mail_handler)

    del main_app.logger.handlers[:]
    if main_app.config.get("ERROR_LOG_PATH"):
        file_handler = get_file_logger_handler(main_app.config.get("ERROR_LOG_PATH"))
        main_app.logger.addHandler(file_handler)
    return main_app


def _init_database(main_app):
    """

    :param main_app:
    :return:
    """

    db.init_app(main_app)
    db.create_all(app=main_app)
    # app.logger.info("Added DB into Application")
    return main_app


def _migrate_database(main_app):
    """

    :param main_app:
    :return:
    """

    migrate = Migrate(main_app, db)
    manager = Manager(main_app)
    manager.add_command('db', MigrateCommand)
    migrate.init_app(main_app, db)
    return main_app


def _create_temp_client():
    """

    :return:
    """

    from .models.models import Client
    try:
        clients = Client.query.all()
        if not clients:
            temp_client = Client()
            temp_client.name = "Testing CIB Client"
            temp_client.email_address = "client_name@client1231.com"
            db.session.add(temp_client)
            db.session.commit()
            # LOGGER.info("Testing client Created successfully")
    except Exception as error:
        print(error)
        # LOGGER.exception(error)


def creating_app(config_class=Config):
    """

    :param config_class:
    :return:
    """

    main_app = Flask(__name__)
    main_app.config.from_object(config_class)
    main_app = _register_blueprints(main_app)
    main_app = _register_login_handlers(main_app)
    main_app.app_context().push()
    return main_app


app = creating_app()
app = _init_database(app)
app = _migrate_database(app)
_create_temp_client()

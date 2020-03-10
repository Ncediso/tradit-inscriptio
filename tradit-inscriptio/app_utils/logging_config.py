
import logging
from flask import Flask, request, render_template
from logging.handlers import SMTPHandler
from flask_login import LoginManager, current_user
from logging import ERROR
from logging.handlers import TimedRotatingFileHandler

# TODO: Use Sentry with Flask on a later stage for logging errors versus emailing them to an email address.


class ContextualFilter(logging.Filter):
    """"""
    def filter(self, log_record):
        """"""
        log_record.url = request.path
        log_record.method = request.method
        log_record.ip = request.environ.get("REMOTE_ADDR")
        # log_record.user_name = None if current_user.is_anonymous else current_user.get_username()
        return True


def get_smtp_logger_handler():
    """"""
    mail_handler = SMTPHandler(
        mailhost='127.0.0.1',
        fromaddr='server-error@example.com',
        toaddrs=['admin@example.com'],
        subject='Application Error'
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    return mail_handler


def get_stream_logger_handler():
    """"""
    stream_handler = logging.StreamHandler()
    log_format = "%(asctime)s\t%(levelname)s\t%(user_id)s\t%(ip)s\t%(method)s\t%(url)s\t%(message)s"
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_file_logger_handler(file_path):
    """"""
    # Only set up a file handler if we know where to put the logs
    # Create one file for each day. Delete logs over 7 days old.
    file_handler = TimedRotatingFileHandler(file_path, when="D", backupCount=7)
    # Use a multi-line format for this logger, for easier scanning
    file_formatter = logging.Formatter('''
    Time: %(asctime)s
    Level: %(levelname)s
    Method: %(method)s
    Path: %(url)s
    IP: %(ip)s
    User ID: %(user_id)s

    Message: %(message)s

    ---------------------''')

    # Filter out all log messages that are lower than Error.
    file_handler.setLevel(ERROR)

    file_handler.setFormatter(file_formatter)
    # file_handler.addFormatter(file_formatter)
    return file_handler

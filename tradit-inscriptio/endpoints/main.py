from flask import render_template, Blueprint, send_from_directory
import os

main = Blueprint('main', __name__)


@main.route('/favicon.ico')
def favicon():
    """"""
    return send_from_directory(
        os.path.join(main.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route('/')
def home():
    """"""
    return render_template('index.html')

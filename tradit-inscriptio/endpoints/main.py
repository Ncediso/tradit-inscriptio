from flask import render_template, Blueprint, send_from_directory, request, jsonify
import os
import uuid
from ..app_utils.forms import DateForm


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


@main.route('/test-form', methods=['post', 'get'])
def get_form():
    form = DateForm()
    if form.validate_on_submit():
        return form.date_field.data.strftime('%x')
    return render_template('forms.html', form=form)


# def create_csv(text):
#     unique_id = str(uuid.uuid4())
#     with open('images/'+unique_id+'.csv', 'a') as file:
#         file.write(text[1:-1]+"\n")
#     return unique_id

from flask_wtf import FlaskForm
from wtforms import DateField


class DateForm(FlaskForm):
    date_field = DateField('Pick a Date', format="%Y%m/%d", id='datepick')

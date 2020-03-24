from flask_wtf import Form
from wtforms import DateField


class DateForm(Form):
    dt = DateField('Pick a Date', format="%Y%m/%d", id='datepick')


from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange,Length
from wtforms.fields.html5 import DateField

class GlobalVariablesForm(FlaskForm):
    capital = IntegerField('Beginning Capital', validators=[DataRequired(),  NumberRange(1_000_0000, 10_000_000_000)])
    leverage = IntegerField('Leverage Ratio', validators=[NumberRange(0, 100)])
    long_leverage = IntegerField('Long Leverage Ratio', validators=[NumberRange(0, 100)])
    short_leverage = IntegerField('Short Leverage Ratio', validators=[NumberRange(0, 100)])
    friction = IntegerField('Internal Friction', validators=[NumberRange(0, 100)])
    submit = SubmitField('Save')

class BackTestForm(FlaskForm):
    name = StringField('Test Name', validators=[DataRequired(), Length(min=2, max=30)])
    start = DateField('Start Date', format='%Y-%m-%d')
    end = DateField('End Date', format='%Y-%m-%d')
    submit = SubmitField('Run & Save')

class BackTestDeleteForm(FlaskForm):
    submit = SubmitField('Delete')


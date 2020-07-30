from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateField

class LoadMarketDataForm(FlaskForm):
    inputfile = FileField('Stock Symbol File (.csv)', validators=[DataRequired(), FileAllowed(['csv'])])

    start = DateField('Start Date', format='%Y-%m-%d')

    end = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])

    submit = SubmitField('Download & Save')

class SpliteStocksForm(FlaskForm):
    inputfile = FileField('Stocks File (.csv)', validators=[DataRequired(), FileAllowed(['csv'])])

    submit = SubmitField('Splite...')

class ImportStocksForm(FlaskForm):
    inputfile = FileField('Stocks File (.csv)', validators=[DataRequired(), FileAllowed(['csv'])])

    submit = SubmitField('Import...')
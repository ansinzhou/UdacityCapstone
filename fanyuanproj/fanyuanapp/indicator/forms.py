from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, BooleanField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange

from fanyuanapp.models import Indicator


class CreateIndicatorForm(FlaskForm):
    name = StringField('Indicator Name', validators=[DataRequired(), Length(min=2, max=30)])
    buyinput = FileField('Buy Indicator File (.csv)', validators=[FileAllowed(['csv'])])
    frombuyfolder = BooleanField('From buy_info folder')
    hongkongstocks = BooleanField('Hong Kong Stocks')
    maxstocks = IntegerField('Max Stocks In Holding', validators=[DataRequired(), NumberRange(1, 1_000)])
    maxdays = IntegerField('Max Days In Holding', validators=[DataRequired(), NumberRange(1, 1_000)])
    target1 = IntegerField('Profit Target1', validators=[DataRequired(), NumberRange(-100, 100)])
    target2 = IntegerField('Profit Target2', validators=[DataRequired(), NumberRange(-100, 100)])
    cutloss = IntegerField('Cut Loss', validators=[DataRequired(), NumberRange(-100, 100)])
    minvolume = IntegerField('Minimum Volumn', validators=[DataRequired(), NumberRange(1, 5_000)])
    minbuy = IntegerField('Minimum Buy', validators=[DataRequired(), NumberRange(1, 500_000_000)])
    tradingfee = FloatField('Trading Fee', validators=[DataRequired(), NumberRange(0.00001, 1)])
    maxtradingfee = FloatField('Max Trading Fee', validators=[DataRequired(), NumberRange(0.00001, 1)])

    submit = SubmitField('create')

    def validate_name(self, name):
        indicator = Indicator.query.filter_by(name=name.data).first()
        if indicator:
            raise ValidationError('That indicator name is taken! Please choose a different one.')

class IndicatorForm(FlaskForm):
    buyinput = FileField('Buy Indicator File (.csv)', validators=[FileAllowed(['csv'])])

    frombuyfolder = BooleanField('From buy_info folder')

    sellinput = FileField('Sell Indicator File (.csv)', validators=[FileAllowed(['csv'])])

    submit = SubmitField('Upload')

class IndicatorVariablesForm(FlaskForm):
    maxstocks = IntegerField('Max Stocks In Holding', validators=[DataRequired(), NumberRange(1, 1_000)])
    maxdays = IntegerField('Max Days In Holding', validators=[DataRequired(), NumberRange(1, 1_000)])
    target1 = IntegerField('Profit Target1', validators=[DataRequired(), NumberRange(-100, 100)])
    target2 = IntegerField('Profit Target2', validators=[DataRequired(), NumberRange(-100, 100)])
    cutloss = IntegerField('Cut Loss', validators=[DataRequired(), NumberRange(-100, 100)])
    minvolume = IntegerField('Minimum Volumn', validators=[DataRequired(), NumberRange(1, 5_000)])
    minbuy = IntegerField('Minimum Buy', validators=[DataRequired(), NumberRange(1, 500_000_000)])
    tradingfee = FloatField('Trading Fee', validators=[DataRequired(), NumberRange(0.00001, 1)])
    maxtradingfee = FloatField('Max Trading Fee', validators=[DataRequired(), NumberRange(0.00001, 1)])
    hongkongstocks = BooleanField('Hong Kong Stocks')
    submit = SubmitField('Save')

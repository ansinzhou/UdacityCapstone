from flask import Blueprint, render_template, flash, redirect, url_for, request
from fanyuanapp import db
from fanyuanapp.indicator.forms import CreateIndicatorForm, IndicatorForm, IndicatorVariablesForm
from fanyuanapp.models import Indicator, BuyInfo, SellInfo, IndicatorVariables

import fanyuanapp.core.indicator_utils as utils

indicator = Blueprint('indicator', __name__)

@indicator.route('/indicator/create_indicator', methods=['GET', 'POST'])
def create_indicator():
    form = CreateIndicatorForm()
    if form.validate_on_submit():
        indicator_name = form.name.data
        indicator = Indicator(name=indicator_name)
        db.session.add(indicator)
        db.session.commit()
        indicator = Indicator.query.filter_by(name=indicator_name).first()
        hongkongmarket = 1 if form.hongkongstocks.data else 0
        trading_variables = IndicatorVariables(maxstocks=form.maxstocks.data, maxdays=form.maxdays.data, target1=form.target1.data, target2=form.target2.data, cutloss=form.cutloss.data, minvolume=form.minvolume.data, minbuy=form.minbuy.data, tradingfee=form.tradingfee.data, maxtradingfee=form.maxtradingfee.data, hongkongmarket=hongkongmarket, indicator_id=indicator.id)
        db.session.add(trading_variables)
        db.session.commit()
        if form.buyinput.data:
            utils.load_buy_indicator(indicator.id, form.buyinput.data.filename, form.hongkongstocks.data)
        if form.frombuyfolder.data:
            utils.load_buy_info(indicator.id)
        flash('Your indicator have been create.', 'success')
        return redirect(url_for('indicator.indicators'))
    return render_template('create_indicator.html', title='Create Indicator', form=form)

@indicator.route('/indicator/indicator_upload/<int:indicator_id>', methods=['GET', 'POST'])
def indicator_upload(indicator_id):
    form = IndicatorForm()
    if form.validate_on_submit():
        if form.buyinput.data:
            utils.load_buy_indicator(indicator_id, form.buyinput.data.filename)

        if form.frombuyfolder.data:
            utils.load_buy_info(indicator_id)

        if form.sellinput.data:
            utils.load_sell_indicator(indicator_id, form.sellinput.data.filename)

        flash('Your buy indicator have been uploaded.', 'success')
        return redirect(url_for('indicator.oneindicator', indicator_id=indicator_id))
    return render_template('indicator_upload.html', title='Indicator Upload', form=form)

@indicator.route('/indicator/indicators')
def indicators():
    indicators = Indicator.query.all()
    return render_template('indicators.html', title='Indicators', indicators=indicators)

@indicator.route('/indicator/oneindicator/<int:indicator_id>', methods=['GET', 'POST'])
def oneindicator(indicator_id):
    indicator = Indicator.query.get_or_404(indicator_id)

    buy_inputs = BuyInfo.query.order_by(BuyInfo.buydate).filter_by(indicator_id=indicator_id).all()

    sell_inputs = SellInfo.query.order_by(SellInfo.selldate).filter_by(indicator_id=indicator_id).all()

    ind_variables = IndicatorVariables.query.filter_by(indicator_id=indicator_id).first()
    form = IndicatorVariablesForm()
    if form.validate_on_submit():
        if ind_variables:
            ind_variables.maxstocks = form.maxstocks.data
            ind_variables.maxdays = form.maxdays.data
            ind_variables.target1 = form.target1.data
            ind_variables.target2 = form.target2.data
            ind_variables.cutloss = form.cutloss.data
            ind_variables.minvolume = form.minvolume.data
            ind_variables.minbuy = form.minbuy.data
            ind_variables.tradingfee = form.tradingfee.data
            ind_variables.maxtradingfee = form.maxtradingfee.data
            ind_variables.hongkongmarket = 1 if form.hongkongstocks.data else 0
        else:
            ind_variables = IndicatorVariables(maxstocks=form.maxstocks.data, maxdays=form.maxdays.data, target1=form.target1.data, target2=form.target2.data, cutloss=form.cutloss.data, minvolume=form.minvolume.data, minbuy=form.minbuy.data,tradingfee=form.tradingfee.data, maxtradingfee=form.maxtradingfee.data, indicator_id=indicator_id)
            db.session.add(ind_variables)
        db.session.commit()
        flash('Your global variables have been updated.', 'success')
    elif request.method == 'GET':
        if ind_variables:
            form.maxstocks.data = ind_variables.maxstocks
            form.maxdays.data = ind_variables.maxdays
            form.target1.data = ind_variables.target1
            form.target2.data = ind_variables.target2
            form.cutloss.data = ind_variables.cutloss
            form.minvolume.data = ind_variables.minvolume
            form.minbuy.data = ind_variables.minbuy
            form.tradingfee.data = ind_variables.tradingfee
            form.maxtradingfee.data = ind_variables.maxtradingfee
            form.hongkongstocks.data = True if ind_variables.hongkongmarket>0 else False
    return render_template('indicator.html', title='Indicator', indicator=indicator, form=form, buyinputs=buy_inputs, sellinputs=sell_inputs)

@indicator.route('/indicator/delete_indicator/<int:indicator_id>', methods=['GET', 'POST'])
def delete_indicator(indicator_id):
    print("delete_indicator=", indicator_id)
    if request.method == 'POST':
        indicator = Indicator.query.get_or_404(indicator_id)
        for buyinput in indicator.buyinputs:
            db.session.delete(buyinput)
        for variable in indicator.variables:
            db.session.delete(variable)
        for sellinput in indicator.sellinputs:
            db.session.delete(sellinput)
        db.session.delete(indicator)
        db.session.commit()
        flash('Your indicator has been deleted.', 'success')
    return redirect(url_for('indicator.indicators'))

@indicator.route('/indicator/indicator_variables')
def indicator_variables():
    indicator_variables = IndicatorVariables.query.all()
    return render_template('indicator_variables.html', title='Indicator Variables', indicator_variables=indicator_variables)

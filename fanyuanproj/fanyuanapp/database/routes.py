from flask import Blueprint, render_template, flash, redirect, url_for, request

from fanyuanapp.database.forms import LoadMarketDataForm, SpliteStocksForm, ImportStocksForm

from fanyuanapp.models import MarketDataSummery, MarketData

from fanyuanapp import marketdataManager

database = Blueprint('database', __name__)

@database.route('/database/download_marketdata', methods=['GET', 'POST'])
def download_marketdata():
    form = LoadMarketDataForm()
    if form.validate_on_submit():
        print(form.inputfile.data.filename, form.start.data, form.end.data)
        marketdataManager.download_upload_marketdata(form.inputfile.data.filename, form.start.data, form.end.data)
        flash('Sucessfully download market data. Please check if some tickers are not sucessful', 'success')
        return redirect(url_for('database.marketdata_summery'))
    return render_template('download_marketdata.html', title='Download Market Data', form=form)

@database.route('/database/marketdata_summery')
def marketdata_summery():
    summeries = MarketDataSummery.query.order_by(MarketDataSummery.symbol).all()
    total = len(summeries)
    return render_template('marketdata_summery.html', title='Market Data Summery', summeries=summeries, total=total)

@database.route('/database/fail_download_marketdata')
def fail_download_marketdata():
    summeries = MarketDataSummery.query.order_by(MarketDataSummery.symbol).filter(MarketDataSummery.fromdate == None).all()
    total = len(summeries)
    return render_template('fail_download_marketdata.html', title='Market Data Summery', summeries=summeries, total=total)

@database.route('/database/marketdata/<string:symbol>')
def marketdata(symbol):
    marketdata = marketdataManager.upload_marketdata_from_file(symbol)
    return render_template('marketdata.html', title='Market Data Summery', marketdata=marketdata)

@database.route('/database/redownload_marketdata')
def redownload_marketdata():
    total = marketdataManager.redownload_failed_marketdata()
    if total>0:
        flash(f'Sucessfully redownload {total} market data', 'success')
        return redirect(url_for('database.marketdata_summery'))

    flash('None market data has been redownloaded!', 'info')
    return redirect(url_for('database.fail_download_marketdata'))


@database.route('/database/update_marketdata_summery', methods=['GET', 'POST'])
def update_marketdata_summery():
    succ = marketdataManager.update_marketdata_summery()
    if succ:
        flash('Sucessfully create or update all the markey data summeries.', 'success')
    else:
        flash(f'Failed to create or update markey data summeries.', 'danger')
    return redirect(url_for('database.marketdata_summery'))

@database.route('/database/splite_marketdata', methods=['GET', 'POST'])
def splite_marketdata():
    form = SpliteStocksForm()
    if form.validate_on_submit():
        succ = marketdataManager.get_marketdata_from_file(form.inputfile.data.filename)
        if succ:
            flash(f'Sucessfully splite market datas from {form.inputfile.data.filename}.', 'success')
            return redirect(url_for('main.home'))
        else:
            flash(f'Failed to splite market data from {form.inputfile.data.filename}.', 'danger')
    return render_template('splite_marketdata.html', title='Splite Stocks', form=form)

@database.route('/database/import_hk_marketdata', methods=['GET', 'POST'])
def import_hk_marketdata():
    form = ImportStocksForm()
    if form.validate_on_submit():
        succ = marketdataManager.get_hk_marketdata_from_file(form.inputfile.data.filename)
        if succ:
            flash(f'Sucessfully import Hongkong market datas from {form.inputfile.data.filename}.', 'success')
            return redirect(url_for('main.home'))
        else:
            flash(f'Failed to import Hongkong market data from {form.inputfile.data.filename}.', 'danger')
    return render_template('import_marketdata.html', title='Import Hongkong Stocks', form=form)


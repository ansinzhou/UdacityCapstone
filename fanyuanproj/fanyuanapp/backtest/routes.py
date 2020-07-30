from flask import Blueprint, render_template, flash, redirect, url_for, request
from fanyuanapp.backtest.forms import GlobalVariablesForm, BackTestForm,BackTestDeleteForm
from fanyuanapp import db
from fanyuanapp.models import GlobalVariables, Indicator, TestSummery, TradeActivity, TestStatistics, DailyPositions
from fanyuanapp.core.testdata_processor import TestDataProcessor
import fanyuanapp.core.constants as constants
from fanyuanapp.core.graphs import generate_save_plot, generate_save_buy_graph

backtest = Blueprint('backtest', __name__)

@backtest.route('/backtest/global_variables', methods=['GET', 'POST'])
def global_variables():
    globals = GlobalVariables.query.first()
    form = GlobalVariablesForm()
    if form.validate_on_submit():
        globals.capital = form.capital.data
        globals.leverage = form.leverage.data
        globals.long_leverage = form.long_leverage.data
        globals.short_leverage = form.short_leverage.data
        globals.friction = form.friction.data
        db.session.commit()
        flash('Your global variables have been updated.', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.capital.data = globals.capital
        form.leverage.data = globals.leverage
        form.long_leverage.data = globals.long_leverage
        form.short_leverage.data = globals.short_leverage
        form.friction.data = globals.friction
    return render_template('global_variables.html', title='Global Variables', form=form)

@backtest.route('/backtest/test', methods=['GET', 'POST'])
def test():
    form = BackTestForm()
    indicators = Indicator.query.all()
    if request.method == 'POST':
        indicator_ids = request.form.getlist("fortest")
        sellindicators = request.form.getlist("sellindicator")
        name = form.name.data
        startdate = form.start.data.strftime(constants.DATE_FORMAT)
        enddate = form.end.data.strftime(constants.DATE_FORMAT)
        if indicator_ids:
            processor = TestDataProcessor()
            summery_id = processor.compile_testdata(indicator_ids, sellindicators, name, startdate, enddate)
            if summery_id != None and summery_id > 0:
                flash('Successfully run a test.', 'success')
                return redirect(url_for('backtest.test_results', summery_id=summery_id))
            else:
                flash('This test is not successful!', 'danger')
        else:
            flash('No Indicator selected! Please select an indicator by clicking at least one checkbox', 'danger')

    return render_template('test.html', title='Back Test', form=form, indicators=indicators)

@backtest.route('/backtest/test_summery')
def test_summery():
    summeries = TestSummery.query.order_by(TestSummery.date_tested.desc()).all()
    return render_template('test_summery.html', title='Test Summery', summeries=summeries)

@backtest.route('/backtest/test_results/<int:summery_id>')
def test_results(summery_id):
    summery = TestSummery.query.filter_by(id=summery_id).first()
    statistics = TestStatistics.query.filter_by(summery_id=summery_id).first()
    positions = summery.dailypositions
    dailyresults = summery.dailyresults
    activities = TradeActivity.query.order_by(TradeActivity.position).filter_by(summery_id=summery_id).all()
    failedtrades = summery.failedtrades
    graph_url = generate_save_plot(summery)

    buy_graph_url = generate_save_buy_graph(summery)

    return render_template('test_results.html', title='Test Result', statistics=statistics, activities=activities, positions=positions, dailyresults=dailyresults, failedtrades=failedtrades,  graph=graph_url, bar=buy_graph_url)

@backtest.route('/backtest/delete_test_summery/<int:summery_id>', methods=['GET', 'POST'])
def delete_test_summery(summery_id):
    print("delete_test_summery=", summery_id)
    if request.method == 'POST':
        delete_summuery(summery_id)
        flash('Your Test Summery has been deleted.', 'success')
    return redirect(url_for('backtest.test_summery'))

@backtest.route('/backtest/delete', methods=['GET', 'POST'])
def delete():
    form = BackTestDeleteForm()
    summeries = TestSummery.query.all()
    if request.method == 'POST':
        summery_ids = request.form.getlist("fordelete")
        if summery_ids:
            for summery_id in summery_ids:
                delete_summuery(summery_id)

            flash('Selected summeries have been deleted.', 'success')
            return redirect(url_for('backtest.test_summery'))
        else:
            flash('No Summery selected! Please select a summery by clicking at least one checkbox', 'danger')

    return render_template('delete_tests.html', title='Delete Back Test Summeries', form=form, summeries=summeries)

def delete_summuery(summery_id):
    summery = TestSummery.query.get_or_404(summery_id)
    for onestatistics in summery.statistics:
        db.session.delete(onestatistics)
    for oneactivity in summery.activity:
        db.session.delete(oneactivity)
    for dailyresult in summery.dailyresults:
        db.session.delete(dailyresult)
    for dailyposition in summery.dailypositions:
        db.session.delete(dailyposition)
    for failedtrade in summery.failedtrades:
        db.session.delete(failedtrade)
    db.session.delete(summery)
    db.session.commit()
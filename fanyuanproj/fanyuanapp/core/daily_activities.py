import pandas as pd

from fanyuanapp import db

from fanyuanapp.models import TradeActivity, DailyResults, DailyPositions, FailedTrades

import fanyuanapp.core.constants as constants

from fanyuanapp.core.statistics_utils import get_beta_alpha_sharpe, calculate_fortfolio_volatility

class DailyActivities:
    def __init__(self):
        self.trading_activities = pd.DataFrame()
        self.trading_positions = pd.DataFrame()
        self.trading_history = pd.DataFrame()
        self.trading_sellinfo = pd.DataFrame()
        self.trading_failures = pd.DataFrame()

    def get_trading_days(self):
        days = len(self.trading_history.index)
        return days

    def add_acitivity(self, buydate, ticker, buyPrice, num_stocks, salePrice, saleDateStr):
        activity = pd.DataFrame()
        activity[constants.DATE_COLUMN] = buydate
        activity[constants.SYMBOL] = ticker
        activity[constants.BUYPRICE] = buyPrice
        activity[constants.QUANTITY] = num_stocks
        activity[constants.SELLPRICE] = salePrice
        activity[constants.SELLDATE] = saleDateStr
        activity.set_index(constants.DATE_COLUMN, inplace=True)
        if self.trading_activities.empty:
            self.trading_activities = activity
        else:
            self.trading_activities = self.trading_activities.append(activity)

        sellinfo = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
        sellinfo[constants.DATE_COLUMN] = saleDateStr
        sellinfo[constants.SYMBOL_COLUMN] = ticker
        sellinfo[constants.SELLPRICE_COLUMN] = salePrice
        sellinfo.set_index(constants.DATE_COLUMN, inplace=True)
        if self.trading_sellinfo.empty:
            self.trading_sellinfo = sellinfo
        else:
            self.trading_sellinfo = self.trading_sellinfo.append(sellinfo)


    def save_dailyactivities(self, summery_id):
        full_filename = '{}/trade_results.csv'.format(constants.USERDATA_FOLDER)
        self.trading_activities.to_csv(full_filename, index=True)

        full_filename = '{}/sell_indicator.csv'.format(constants.USERDATA_FOLDER)
        self.trading_sellinfo.sort_values([constants.DATE_COLUMN])
        self.trading_sellinfo.to_csv(full_filename, index=True)

        for row_index, row in self.trading_activities.iterrows():
            buyActivity = TradeActivity(
                position=row_index,
                symbol=row[constants.SYMBOL],
                tranaction='Buy',
                unitprice=row[constants.BUYPRICE],
                quantity=row[constants.QUANTITY],
                summery_id=summery_id)
            db.session.add(buyActivity)
            sellActivity = TradeActivity(
                position=row[constants.SELLDATE],
                symbol=row[constants.SYMBOL],
                tranaction='Sell',
                unitprice=row[constants.SELLPRICE],
                quantity=-row[constants.QUANTITY],
                summery_id=summery_id)
            db.session.add(sellActivity)
        db.session.commit()

    def is_noactivity(self):
        return self.trading_activities.empty

    def add_daily_results(self, dateStr, dailyTrades, middle_results):
        hist_result = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
        hist_result[constants.DATE_COLUMN] = dateStr
        hist_result[constants.CASH] = "%.2f" % middle_results.cash
        hist_result[constants.HOLDING] = "%.2f" % middle_results.holdingValue
        hist_result[constants.ACTUALPORTFOLIO] = "%.2f" % middle_results.actualPortfolio
        hist_result[constants.PORTFOLIO] = "%.2f" % middle_results.portfolio
        hist_result[constants.LEVERAGE] = "%.2f" % middle_results.get_leverage_usage()
        hist_result[constants.DRAWDOWN] = "%.4f" % middle_results.drawdown
        hist_result[constants.BOUGHT] = "%d" % dailyTrades
        hist_result[constants.RETURNS] = middle_results.returns
        hist_result.set_index(constants.DATE_COLUMN, inplace=True)
        if self.trading_history.empty:
            self.trading_history = hist_result
        else:
            self.trading_history = self.trading_history.append(hist_result)

    def calculate_beta_aphla_sharpe(self, start, end, ishongkongstock):
        return get_beta_alpha_sharpe(self.trading_history, start, end, ishongkongstock)

    def calculate_portfolio_volatility(self):
        # (portfolio, volatility) = calculate_fortfolio_volatility(self.trading_history)
        # self.volatility = volatility
        self.volatility = 'NA'


    def save_dailyresults(self, summery_id):

        full_filename = '{}/trade_hist.csv'.format(constants.USERDATA_FOLDER)
        self.trading_history.to_csv(full_filename, index=True)

        for row_index, row in self.trading_history.iterrows():
            testdetails = DailyResults(date=row_index,
                                         cash=row[constants.CASH],
                                         holding=row[constants.HOLDING],
                                         actualportfolio=row[constants.ACTUALPORTFOLIO],
                                         portfolio=row[constants.PORTFOLIO],
                                         leverage=row[constants.LEVERAGE],
                                         drawdown=row[constants.DRAWDOWN],
                                         boughtstocks=row[constants.BOUGHT],
                                         returns=row[constants.RETURNS],
                                         summery_id=summery_id)
            db.session.add(testdetails)

        db.session.commit()

    def add_position(self, tradingdate, ticker, unitPrice, quantity, holdingvalue, period, gainloss):

        position = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
        position[constants.DATE_COLUMN] = tradingdate
        position[constants.SYMBOL] = ticker
        position[constants.UNITPRICE] = unitPrice
        position[constants.QUANTITY] = quantity
        position[constants.POSITION] = holdingvalue
        position[constants.PERIOD] = period
        position[constants.GAIN_LOSS] = gainloss
        position.set_index(constants.DATE_COLUMN, inplace=True)
        if self.trading_positions.empty:
            self.trading_positions = position
        else:
            self.trading_positions = self.trading_positions.append(position)

    def save_dailypositions(self, summery_id):
        full_filename = '{}/trade_positions.csv'.format(constants.USERDATA_FOLDER)
        self.trading_positions.to_csv(full_filename, index=True)

        for row_index, row in self.trading_positions.iterrows():
            dailyposition = DailyPositions(date=row_index,
                                         symbol=row[constants.SYMBOL],
                                         unitprice=row[constants.UNITPRICE],
                                         quantity=row[constants.QUANTITY],
                                         position=row[constants.POSITION],
                                         period=row[constants.PERIOD],
                                         gainloss=row[constants.GAIN_LOSS],
                                         summery_id=summery_id)
            db.session.add(dailyposition)
        db.session.commit()

    def add_failure(self, tradingdate, ticker, reason):

        failure = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
        failure[constants.DATE_COLUMN] = tradingdate
        failure[constants.SYMBOL] = ticker
        failure[constants.FAIL_REASON] = reason
        failure.set_index(constants.DATE_COLUMN, inplace=True)
        if self.trading_failures.empty:
            self.trading_failures = failure
        else:
            self.trading_failures = self.trading_failures.append(failure)

    def save_failed_trades(self, summery_id):
        full_filename = '{}/trade_failures.csv'.format(constants.USERDATA_FOLDER)
        self.trading_failures.to_csv(full_filename, index=True)

        for row_index, row in self.trading_failures.iterrows():
            dailyposition = FailedTrades(date=row_index,
                                          symbol=row[constants.SYMBOL],
                                          reason=row[constants.FAIL_REASON],
                                          summery_id=summery_id)
            db.session.add(dailyposition)
        db.session.commit()

    def save_activities(self, summery_id):
        self.save_dailyresults(summery_id)
        self.save_dailyactivities(summery_id)
        self.save_dailypositions(summery_id)
        self.save_failed_trades(summery_id)
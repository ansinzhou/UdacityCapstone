import pandas as pd
from fanyuanapp import db
import fanyuanapp.core.constants as constants
from fanyuanapp.models import TestSummery, TestStatistics


class MiddleResults:

    def __init__(self, name, indicators, cash, leverage, longLeverage, shortLeverage):
        self.name = name
        self.indicators=indicators
        self.totalCash = cash
        self.cash = cash
        self.portfolio = cash
        self.actualPortfolio = cash
        self.originalLeverage = leverage if longLeverage == 0 and shortLeverage == 0 else 0
        self.leverage = leverage if longLeverage == 0 and shortLeverage == 0 else 0
        self.orignalLongLeverage = longLeverage
        self.longLeverage = longLeverage
        self.orignalShortLeverage = shortLeverage
        self.shortLeverage = shortLeverage
        self.returns = 0
        self.cashused = 0
        self.dailycashused = 0
        self.leverageused = 0
        self.dailyleverageused = 0
        self.holdingvalue = 0
        self.holdings = 0
        self.dailyholdings = 0
        self.holdingperiod = 0
        self.drawdown = 0
        self.maxdrawdown = 0
        self.lowestpoint = 1

        self.invalid_inputs = pd.DataFrame()
        self.dailyTrades=0
        self.totalActualTrades = 0
        self.totalPotentialTrades = 0
        self.noTradeForVolume = 0
        self.noTradeForShortCash = 0
        self.totalWins = 0
        self.totalLoss=0
        self.largestLostSale = 0
        self.notFoundTickersInMarket = set()
        self.totalFailuresToBuyStocks = 0
        self.largestLostSale = 0

    def add_cash(self, cashfromsold):
        self.cash += cashfromsold

    def remove_cash(self, cashforbuy):
        self.cash -= cashforbuy

    def get_max_leverage(self, isShort):
        if self.originalLeverage > 0:
            return self.originalLeverage
        elif isShort:
            return self.orignalShortLeverage
        else:
            return self.orignalLongLeverage

    def get_leverage(self, isShort):
        if self.originalLeverage > 0:
            return self.leverage
        elif isShort:
            return self.shortLeverage
        else:
            return self.longLeverage

    def get_leverage_usage(self):
        if self.originalLeverage > 0:
            return self.originalLeverage - self.leverage
        else:
            return (self.orignalLongLeverage + self.orignalShortLeverage) - (self.longLeverage + self.shortLeverage)

    def add_leverage(self, leveragefromsold, isShort):
        if self.originalLeverage > 0:
            self.leverage += leveragefromsold
        elif isShort:
            self.shortLeverage += leveragefromsold
        else:
            self.longLeverage += leveragefromsold

    def remove_leverage(self, leverageforbuy, isShort):
        self.dailyleverageused += leverageforbuy
        if self.originalLeverage > 0:
            self.leverage -= leverageforbuy
        elif isShort:
            self.shortLeverage -= leverageforbuy
        else:
            self.longLeverage -= leverageforbuy

    def increase_cashused_holdings(self, investcash):
        self.dailycashused += investcash
        self.dailyholdings += 1
        self.dailyTrades += 1

    def decrease_cashused_holdings(self, investcash):
        self.dailycashused -= investcash
        self.dailyholdings -= 1

    def increase_fail_buy_stock_with_error(self):
        self.totalFailuresToBuyStocks += 1

    def add_not_found_in_market_data(self, ticker):
        self.notFoundTickersInMarket.add(ticker)

    # def get_trading_days(self):
    #     days = len(self.trading_history.index)
    #     return days

    def calculate_returns(self):
        p_return = (float(self.actualPortfolio)-float(self.totalCash))/float(self.totalCash)
        self.returns = round(p_return, 5)
        if self.returns < self.lowestpoint:
            self.lowestpoint = self.returns

    def calculate_portfolio_drawdown_with(self, holdingValue):
        self.portfolio = self.cash + holdingValue
        leverageUsage = self.get_leverage_usage()
        newActualPortfolio = self.portfolio - leverageUsage
        if self.actualPortfolio > newActualPortfolio:
            self.drawdown = ((self.actualPortfolio - newActualPortfolio)/float(self.portfolio))
            if self.drawdown > self.maxdrawdown:
                self.maxdrawdown = self.drawdown
        else:
            self.drawdown = 0

        self.actualPortfolio = newActualPortfolio
        self.calculate_returns()

    def decide_win_or_loss(self, buyprice, saleprice, num_stocks, isShortAction):
        lost = 0
        if float(saleprice) > float(buyprice):
            if isShortAction:
                self.totalLoss += 1
                lost = (float(saleprice) - float(buyprice))*num_stocks
            else:
                self.totalWins += 1
        else:
            if isShortAction:
                self.totalWins += 1
            else:
                self.totalLoss += 1
                lost = (float(buyprice) - float(saleprice))*num_stocks
        if (lost > self.largestLostSale):
            self.largestLostSale = lost

    def is_invalid_input(self, ticker, buyDateStr, buyPrice, high_price, low_price):
        buy_price = float(buyPrice)
        if (buy_price < low_price or buy_price > high_price):
            invalid_input = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
            invalid_input[constants.DATE_COLUMN] = buyDateStr
            invalid_input['Stock'] = ticker
            invalid_input['Buy Price'] = buyPrice
            invalid_input[constants.HIGH_COLUMN] = high_price
            invalid_input[constants.LOW_COLUMN] = low_price
            invalid_input.set_index(constants.DATE_COLUMN, inplace=True)
            print(invalid_input)
            if self.invalid_inputs.empty:
                self.invalid_inputs = invalid_input
            else:
                self.invalid_inputs = self.invalid_inputs.append(invalid_input)
            return True
        return False

    def process_sell_stock(self, moneyFromSoldStock, moneyForBuyStock, holdingDays, isShort):
        self.holdingperiod += holdingDays
        maxLeverage = self.get_max_leverage(isShort)
        leverage = self.get_leverage(isShort)

        if (maxLeverage > leverage):
            if (maxLeverage > (leverage + moneyFromSoldStock)):
                self.add_leverage(moneyFromSoldStock, isShort)
            else:
                leverageGain = (maxLeverage - leverage)
                self.add_leverage(leverageGain, isShort)
                cashFromStock = moneyFromSoldStock - leverageGain
                self.add_cash(cashFromStock)
                self.decrease_cashused_holdings(cashFromStock)
        else:
            self.add_cash(moneyFromSoldStock)
            self.decrease_cashused_holdings(moneyForBuyStock)

    def process_daily_results(self, holdingValue):
        self.holdingValue = holdingValue
        self.calculate_portfolio_drawdown_with(holdingValue)
        self.cashused += self.dailycashused
        self.leverageused += self.dailyleverageused
        self.holdings += self.dailyholdings
        self.totalActualTrades += self.dailyTrades
        self.dailyTrades = 0

    def build_and_save_test_summery(self, start, end, beta, alpha, sharpe, trading_days, ishongkongstock):
        summery = pd.DataFrame([1], columns=['DateRange'])
        summery[constants.START] = start
        summery[constants.END] = end
        summery[constants.TRADES] = "%d" % self.totalActualTrades
        summery[constants.NOTRADESFORVOLUME] = "%d" % self.noTradeForVolume
        summery[constants.NOTRADESFORCASH] = "%d" % self.noTradeForShortCash
        summery[constants.POTENTIALTRADES] = "%d" % self.totalPotentialTrades
        summery[constants.LOSTSALE] = "%d" % self.largestLostSale
        summery[constants.WINS] = self.display_percentage(self.totalWins/self.totalActualTrades)
        summery[constants.LOSS] = self.display_percentage(self.totalLoss/self.totalActualTrades)
        summery[constants.COVERAGE] = self.display_percentage(self.totalActualTrades/(self.totalActualTrades+self.noTradeForShortCash))
        summery[constants.DRAWDOWN] = self.display_percentage(self.maxdrawdown)
        summery[constants.LOWESTPOINT] = self.display_percentage(self.lowestpoint)
        summery[constants.RETURNS] = self.display_percentage(self.returns)
        summery[constants.BETA] = beta
        summery[constants.ALPHA] = alpha
        summery[constants.SHARPE] = sharpe
        summery[constants.TURNOVER] = "%.2f" % ((float(self.totalCash) + self.portfolio)/2)
        summery[constants.LEVERAGE] = "%.2f" % (self.leverageused / trading_days)
        summery[constants.CASHUSED] = "%.2f" % (self.cashused / trading_days)
        summery[constants.HOLDINGS] = "%.2f" % (self.holdings/ trading_days)
        summery[constants.PERIOD] = "%.2f" % (self.holdingperiod/self.totalActualTrades)
        summery[constants.VOLATILITY] = 'NA'

        full_filename = '{}/trade_summery.csv'.format(constants.USERDATA_FOLDER)
        summery.to_csv(full_filename, index=True)

        full_filename = '{}/invalid_inputs.csv'.format(constants.USERDATA_FOLDER)
        self.invalid_inputs.to_csv(full_filename, index=True)

        return self.save_testsummery(summery, ishongkongstock)

    def save_testsummery(self, summery, ishongkongstock):
        hongkongmarket = 1 if ishongkongstock else 0
        testsummery = TestSummery(name=self.name,
                                  start=summery.at[0, constants.START],
                                  end=summery.at[0, constants.END],
                                  indicators=self.indicators,
                                  returns=summery.at[0,constants.RETURNS],
                                  status='Completed',
                                  hongkongmarket=hongkongmarket)
        db.session.add(testsummery)
        db.session.commit()

        testsummery = TestSummery.query.order_by(TestSummery.date_tested.desc()).first()
        testStatistics = TestStatistics(trades=summery.at[0, constants.TRADES],
                                        notradesforvolume=summery.at[0,constants.NOTRADESFORVOLUME],
                                        notradesforcash=summery.at[0,constants.NOTRADESFORCASH],
                                        potentialtrades=summery.at[0,constants.POTENTIALTRADES],
                                        lostsale=summery.at[0,constants.LOSTSALE],
                                        wins=summery.at[0,constants.WINS],
                                        loss=summery.at[0,constants.LOSS],
                                        coverage=summery.at[0,constants.COVERAGE],
                                        drawdown=summery.at[0,constants.DRAWDOWN],
                                        lowestpoint=summery.at[0,constants.LOWESTPOINT],
                                        returns=summery.at[0,constants.RETURNS],
                                        beta=summery.at[0,constants.BETA],
                                        alpha=summery.at[0,constants.ALPHA],
                                        sharpe=summery.at[0,constants.SHARPE],
                                        turnover=summery.at[0,constants.TURNOVER],
                                        leverage=summery.at[0,constants.LEVERAGE],
                                        cashused=summery.at[0,constants.CASHUSED],
                                        holdings=summery.at[0,constants.HOLDINGS],
                                        period=summery.at[0,constants.PERIOD],
                                        volatility=summery.at[0,constants.VOLATILITY],
                                        summery_id=testsummery.id)
        db.session.add(testStatistics)
        db.session.commit()
        # print("testsummery:", testsummery)

        return testsummery.id

    def display_percentage(self, pct):
        pct_str = "%.2f" % (pct*100)
        return f'{pct_str}'

    def __repr__(self):
        return  f"MiddleResults({self.totalCash},{self.cash},{self.holdingvalue},{self.portfolio},{self.returns},{self.drawdown},{self.cashused},{self.dailycashused},{self.holdings},{self.dailyholdings},{self.holdingperiod})"

import pandas as pd
import datetime as dt
pd.core.common.is_list_like = pd.api.types.is_list_like
import math
import time
import traceback

import fanyuanapp.core.constants as constants
import fanyuanapp.core.parameters_util as params
import fanyuanapp.core.backtest_utils as utils

from fanyuanapp import marketdataManager
from fanyuanapp.core.test_middle_results import MiddleResults
from fanyuanapp.core.daily_activities import DailyActivities
from fanyuanapp import app, logger

class TestDataProcessor:
    def __init__(self):
        self.investedStocks = dict()
        self.stocksSaleInfo = dict()
        self.soldStocks = dict()
        self.shortStocks = dict()

    @staticmethod
    def generate_save_plot(summery):
        return utils.generate_save_plot(summery)

    def get_holding_value(self, tradeDate, daily_activities):
        totalHoldingValue = 0
        prev4Days = tradeDate - dt.timedelta(days=6)
        prev1Days = tradeDate - dt.timedelta(days=1)
        startDate = prev4Days
        endDate = prev1Days
        for ticker in self.investedStocks.keys():
            (numStocks, holdingDays, isShortProcess) = self.investedStocks[ticker]
            if numStocks > 0:
                data = marketdataManager.get_market_data(ticker, startDate, endDate, False)
                if data.empty:
                    err_msg = f'no market data for {ticker} before {tradeDate}'
                    print(err_msg)
                    logger.info(err_msg)
                    continue

                firstRow = data.head(1)
                closePrice = float(firstRow[constants.CLOSE_COLUMN])
                holdingValue = (numStocks*float(closePrice))
                (soldDate, moneyFromSoldStock, moneyForBuyStock) = self.stocksSaleInfo[ticker]
                if isShortProcess:
                    holdingValue = moneyForBuyStock - holdingValue + moneyForBuyStock
                totalHoldingValue += holdingValue
                gainloss = holdingValue - moneyForBuyStock
                period = holdingDays + 1
                self.investedStocks[ticker] = (numStocks, period, isShortProcess)
                tradeDateStr = tradeDate.strftime(constants.DATE_FORMAT)
                daily_activities.add_position(tradeDateStr, ticker, closePrice, numStocks, holdingValue, period, gainloss)
        return totalHoldingValue

    def processSellStocks(self, startDate, endDate, middle_results, daily_activities):

        histDate = startDate

        while (histDate.date() < endDate.date()):
            if (histDate.weekday()==5):
                histDate = histDate + dt.timedelta(days=2)
                continue

            histDateStr = histDate.strftime(constants.OUTPUT_DATE_FORMAT)
            if marketdataManager.is_business_day(histDateStr) == False:
                print("Holiday:", histDateStr)
                histDate = histDate + dt.timedelta(days=1)
                continue

            dailySold = 0
            for soldticker in self.stocksSaleInfo.keys():
                (soldDate, moneyFromSoldStock, moneyForBuyStock) = self.stocksSaleInfo[soldticker]
                if soldDate == histDateStr:
                    dailySold += moneyFromSoldStock
                    (numStocks, holdingDays, isShortProcess) = self.investedStocks[soldticker]
                    self.investedStocks[soldticker] = (0, 0, False)
                    middle_results.process_sell_stock(moneyFromSoldStock, moneyForBuyStock, holdingDays, isShortProcess)
                    log_info = f'{histDateStr}: Sold {soldticker} / {"%.2f" % moneyFromSoldStock}'
                    logger.info(log_info)

            log_info = f'{histDateStr}: Daily Total Sold:{"%.2f" % dailySold}'
            logger.info(log_info)
            # logger.info(log_info)

            totalSoldMoney = self.soldStocks.get(histDateStr)
            log_info = f'{histDateStr}: Inconsitent cash from daily sold {dailySold} to record {totalSoldMoney}'
            if dailySold == 0  and totalSoldMoney != None:
                print(log_info)
                logger.info(log_info)
            elif dailySold > 0  and totalSoldMoney == None:
                print(log_info)
                logger.info(log_info)
            elif (totalSoldMoney != None and ((dailySold > float(totalSoldMoney) + 1) or (dailySold < float(totalSoldMoney) - 1))):
                print(log_info)
                logger.info(log_info)

            holdingValue = self.get_holding_value(histDate, daily_activities)
            if (holdingValue > 40000000):
                print('Too large holding value: {}'.format(holdingValue))

            # get dailyTrade value now otherwise it will be reset in process_daily_results
            dailyTrades = middle_results.dailyTrades
            middle_results.process_daily_results(holdingValue)
            daily_activities.add_daily_results(histDateStr, dailyTrades, middle_results)

            log_info = f'{histDateStr}: Daily Info: holding={"%.2f" % holdingValue}, cash={"%.2f" % middle_results.cash}, portfolio={"%.2f" % middle_results.portfolio}'
            logger.info(log_info)

            histDate = histDate + dt.timedelta(days=1)

    def get_input_after_init(self, indicator_ids, sell_indicators, startdate, enddate):
        start_time = time.perf_counter()
        input = pd.DataFrame()

        try:
            # logfilepath = app.config.get('LOG_FILE_NAME')
            # os.remove(logfilepath)

            log_info = f'Load all buy parameters'
            logger.info(log_info)
            params.load_buyparameters(indicator_ids)

            ishkstock = params.is_hongkong_stock()

            log_info = f'Start to load buyindicators with ids {indicator_ids} from {startdate} to {enddate}'
            print(log_info)
            logger.info(log_info)
            input = utils.load_buyindicators(indicator_ids, startdate, enddate)
            if input.empty:
                print("Cannot process testdata without input indicator!!!")
                return input

            current_time = dt.datetime.now()
            log_info = "Finished to load buy indicators"
            print(log_info, current_time)
            logger.info(log_info)

            log_info = f'Start to load marketdata from {startdate} to {enddate}'
            print(log_info)
            logger.info(log_info)

            symbols = set(input[constants.SYMBOL_COLUMN])
            # if marketdataManager.load_market_data(symbols, startdate, enddate) == False:
            if marketdataManager.load_market_data_from_stock_dfs(symbols, startdate, enddate) == False:
                print("Cannot process testdata without marketdata!!!")
                return input

            marketdataManager.load_business_days(startdate, enddate, ishkstock)

            log_info = "Finished to load marketdata"
            current_time = dt.datetime.now()
            print(log_info, current_time)
            logger.info(log_info)

            self.investedStocks.clear()
            self.stocksSaleInfo.clear()
            self.soldStocks.clear()

        except Exception:
            print("Exception for initialing ")
            logger.exception(f'Exceptiion for initialing test')
            traceback.print_exc()

        end_time = time.perf_counter()
        time_taken = (end_time - start_time)/60.0
        latency = '\nTotal initial test time: {:6.2f}'.format(time_taken)
        print(latency)

        return input

    def compile_testdata(self, indicator_ids, sell_indicators, name, startdate, enddate):
        current_time = dt.datetime.now()
        log_info = f'compile_testdata: {startdate} to {enddate} indcators={indicator_ids}, sell_indicators={sell_indicators}'
        print(log_info, current_time)
        logger.info(log_info)

        input = self.get_input_after_init(indicator_ids, sell_indicators, startdate, enddate)
        if input.empty:
            log_info = f'Input is empty'
            print(log_info, current_time)
            logger.info(log_info)
            return 0

        start_time = time.perf_counter()

        daily_activities = DailyActivities()

        currentProcessDate = None
        lastSoldDate = None
        totalCash = params.get_total_cash()
        (originalLeverage, originalLongLeverage, originalShortLeverage) = params.get_leverages(totalCash)
        prevBuyDateStr = ''
        indicators = utils.get_indicator_names(indicator_ids)
        middle_results = MiddleResults(name, indicators, float(totalCash), float(originalLeverage), float(originalLongLeverage), float(originalShortLeverage))


        log_info = f'start to process with total {totalCash}$ ...'
        logger.info(log_info)
        print(log_info)

        start_date = dt.datetime.strptime(startdate, constants.DATE_FORMAT)

        # print("input=", input)
        for row_index, row in input.iterrows():
            ticker = row[constants.SYMBOL_COLUMN]
            indicator_id = row[constants.INDICATOR_COLUMN]
            isShortProcess = params.is_short_parameters(indicator_id)
            if marketdataManager.is_marketdata_available(ticker) == False:
                middle_results.add_not_found_in_market_data(ticker)
                continue

            buyDateStr = row[constants.DATE_COLUMN]
            buyPrice = row[constants.BUYPRICE_COLUMN]
            buyDate = dt.datetime.strptime(buyDateStr, constants.DATE_FORMAT)
            print(f'buy: {ticker}/{buyDateStr}/{buyPrice}')
            try:
                if currentProcessDate == None:
                    currentProcessDate = buyDate
                    # print("The first trading day ", currentProcessDate)
                    lastSoldDate = currentProcessDate
                    prevBuyDateStr = buyDateStr
                    if (currentProcessDate.date() > start_date.date()):
                        self.processSellStocks(start_date, currentProcessDate, middle_results, daily_activities)
                elif buyDate != currentProcessDate:
                    prevBuyDate = dt.datetime.strptime(prevBuyDateStr, constants.DATE_FORMAT)
                    currentProcessDate = buyDate
                    if (currentProcessDate.date() > lastSoldDate.date()):
                        lastSoldDate = currentProcessDate

                    self.processSellStocks(prevBuyDate, currentProcessDate, middle_results, daily_activities)
                    prevBuyDateStr = buyDateStr

                if math.isnan(float(buyPrice)) or buyPrice == 0:
                    continue

                if (ticker in self.stocksSaleInfo):
                    (num_stocks, period, shortStock) = self.investedStocks.get(ticker)
                    if (num_stocks != None and num_stocks>0):
                        (soldDate, moneyFromSoldStock1, moneyForInvest) = self.stocksSaleInfo[ticker]
                        log_info = f'Cannot buy stock because {ticker} has been bought in {soldDate}'
                        print(log_info)
                        logger.info(log_info)
                        middle_results.increase_fail_buy_stock_with_error()
                        continue

                availableInvestPerStock = params.invest_money_per_stock(indicator_id, middle_results.actualPortfolio)
                # print("availableInvestPerStock=", availableInvestPerStock)

                holdlingDays = params.get_max_holding_days(indicator_id)
                marketData = marketdataManager.get_market_data_from(ticker, buyDate, holdlingDays)
                if marketData.empty:
                    log_info = f'Cannot buy stock because No market data for {ticker} from {buyDate} in {holdlingDays}'
                    print(log_info)
                    logger.info(log_info)
                    middle_results.increase_fail_buy_stock_with_error()
                    continue

                queryDate = buyDate.strftime(constants.DATE_FORMAT)
                mkdata_row = marketData.loc[marketData[constants.DATE_COLUMN] == queryDate]
                if mkdata_row.empty:
                    log_info = f'Cannot buy stock because of No market data for {ticker} in {buyDate}'
                    print(log_info)
                    logger.info(log_info)
                    middle_results.increase_fail_buy_stock_with_error()
                    continue

                if len(mkdata_row.index)>1:
                    log_info = f'Has duplicated market data for {ticker} in {buyDate}'
                    print(log_info)
                    logger.info(log_info)
                    # middle_results.increase_fail_buy_stock_with_error()
                    continue

                high_price = float(mkdata_row[constants.HIGH_COLUMN]) + 0.5
                low_price = float(mkdata_row[constants.LOW_COLUMN]) - 0.05
                if middle_results.is_invalid_input(ticker, buyDateStr, buyPrice, high_price, low_price):
                    log_info = f'Cannot buy stock because invalid price {buyPrice} compared with high {high_price} and low {low_price}'
                    print(log_info)
                    logger.info(log_info)
                    middle_results.increase_fail_buy_stock_with_error()
                    continue

                minVolPercent = params.get_minimum_volumn_percent  (indicator_id)
                minTradeVolumn = marketdataManager.previous_min_total_trade(ticker, buyDate, minVolPercent)
                if minTradeVolumn == 0:
                    log_info = f'Cannot buy stock because cannot found Market Data before {buyDate} for {ticker}'
                    logger.info(log_info)
                    continue

                middle_results.totalPotentialTrades += 1

                (num_stocks, totalInvest) = params.buy_stocks(indicator_id, buyPrice, minTradeVolumn, middle_results.portfolio)
                # print(f'buy_stocks: {num_stocks}/{totalInvest}')
                if num_stocks <= 0:
                    daily_activities.add_failure(buyDateStr, ticker, 'Small Volume')
                    middle_results.noTradeForVolume += 1
                    continue

                # print('Cash: {} and investPerStock:{}'.format(availableCash, totalInvest))
                leverageMoney = middle_results.get_leverage(isShortProcess)
                if ((middle_results.cash <= availableInvestPerStock) and (leverageMoney<=availableInvestPerStock)):
                    # print('No enough money to buy stock today {} and cash: {} and investPerStock:{}'.format(buyDateStr, availableCash, availableInvestPerStock))
                    daily_activities.add_failure(buyDateStr, ticker, 'Short Cash')
                    middle_results.noTradeForShortCash += 1
                    continue

                totalNeedMoney = totalInvest
                cashNeeded = 0
                leverageNeeded = 0
                if (middle_results.cash>=totalNeedMoney):
                    self.investedStocks[ticker] = (num_stocks, 0, isShortProcess)
                    cashNeeded = totalNeedMoney
                    # print('availableCash:{}'.format(availableCash))
                    # print('num_stocks={}, totalInvest={}'.format(num_stocks, totalInvest))
                elif (leverageMoney > (totalNeedMoney - middle_results.cash)):
                    leverageNeeded = (totalNeedMoney - middle_results.cash)
                    cashNeeded = middle_results.cash
                    self.investedStocks[ticker] = (num_stocks, 0, isShortProcess)
                    # print('leverageMoney:{}'.format(leverageMoney))
                    # print('num_stocks={}, totalInvest={}'.format(num_stocks, totalInvest))
                else:
                    daily_activities.add_failure(buyDateStr, ticker, 'Short Cash')
                    middle_results.noTradeForShortCash += 1
                    log_info = f'no money left for {buyDateStr}'
                    print(log_info)
                    logger.info(log_info)
                    continue


                idstr = f'{indicator_id}'
                use_sell_indicator = idstr in sell_indicators
                (saleDateStr, salePrice) = utils.get_sale_price_date(indicator_id, use_sell_indicator, ticker, buyDateStr, buyPrice, marketData)
                # print(f'{ticker} salePrice={salePrice}, saleDate={saleDateStr}')

                if salePrice < 0.001:
                    self.investedStocks[ticker] = (0, 0, False)
                    continue

                middle_results.remove_cash(cashNeeded)
                middle_results.remove_leverage(leverageNeeded, isShortProcess)
                middle_results.increase_cashused_holdings(cashNeeded)

                totalSold = 0.0
                if any(self.soldStocks.items()):
                    sold = self.soldStocks.get(saleDateStr)
                    if sold != None:
                        totalSold = float(sold)

                middle_results.decide_win_or_loss(buyPrice, salePrice, num_stocks, isShortProcess)

                finalSalePrice = utils.get_final_sale_price(isShortProcess, salePrice, buyPrice)

                moneyFromSold = finalSalePrice*num_stocks
                self.soldStocks[saleDateStr] = totalSold + moneyFromSold
                self.stocksSaleInfo[ticker]=(saleDateStr, moneyFromSold, totalNeedMoney)
                log_info = f'{buyDateStr}: Bought {ticker} / {buyPrice} / {num_stocks} / {"%.2f" % totalNeedMoney}'
                logger.info(log_info)
                log_info = f'{buyDateStr}: Expect to sell {ticker} / {salePrice} / -{num_stocks} / {"%.2f" % moneyFromSold} / {saleDateStr}'
                logger.info(log_info)

                daily_activities.add_acitivity(mkdata_row[constants.DATE_COLUMN], ticker, buyPrice, num_stocks, salePrice, saleDateStr)
                
                saleDate = dt.datetime.strptime(saleDateStr, constants.DATE_FORMAT)
                if (saleDate.date() > lastSoldDate.date()):
                    lastSoldDate = saleDate

            except Exception:
                print("Exception for processing ", ticker, buyDateStr)
                logger.exception(f'Exceptiion for processing {ticker} in {buyDateStr}')
                traceback.print_exc()
                break

        if daily_activities.is_noactivity():
            print('No results!')
            logger.info('No results!')
            return 0

        print('Last Buy Date: {}, Last Sold Date: {}'.format(currentProcessDate.strftime(constants.OUTPUT_DATE_FORMAT), lastSoldDate.strftime(constants.OUTPUT_DATE_FORMAT)))
        lasttradedate = lastSoldDate.strftime(constants.OUTPUT_DATE_FORMAT)
        lastSoldDate = lastSoldDate + dt.timedelta(days=1)
        self.processSellStocks(currentProcessDate, lastSoldDate, middle_results, daily_activities)
        log_info = f'finished to process data from {startdate} to {lasttradedate}'
        logger.info(log_info)

        test_summery_id = self.finalize_result(startdate, lasttradedate, daily_activities,  middle_results)

        end_time = time.perf_counter()
        time_taken = (end_time - start_time)/60.0
        latency = '\nTotal time: {:6.2f}'.format(time_taken)
        print(latency)
        logger.info(f'finished to save results with time {"%.2f" % time_taken}')

        return test_summery_id

    def finalize_result(self, startdate, lasttradedate, daily_activities, middle_results):
        start_time = time.perf_counter()
        test_summery_id = 0

        try:
            logger.info('Start to finalize test results')

            # daily_activities.calculate_portfolio_volatility()

            trading_days = daily_activities.get_trading_days()
            (beta, alpha, sharpe) = daily_activities.calculate_beta_aphla_sharpe(startdate, lasttradedate, params.is_hongkong_stock())
            test_summery_id = middle_results.build_and_save_test_summery(startdate, lasttradedate, beta, alpha, sharpe, trading_days, params.is_hongkong_stock())

            daily_activities.save_activities(test_summery_id)

            for ticker in middle_results.notFoundTickersInMarket:
                log_info = f'No Market Data for {ticker}'
                print(log_info)
                logger.info(log_info)

            if middle_results.totalFailuresToBuyStocks>0:
                info_msg = f'Total {middle_results.totalFailuresToBuyStocks} failures to buy stocks'
                print(info_msg)
                logger.info(info_msg)

            
        except Exception:
            print("Exception for initialing ")
            logger.exception(f'Exceptiion for initialing test')
            traceback.print_exc()

        end_time = time.perf_counter()
        time_taken = (end_time - start_time)/60.0
        latency = '\nTotal finalizing result time: {:6.2f}'.format(time_taken)
        print(latency)

        return test_summery_id

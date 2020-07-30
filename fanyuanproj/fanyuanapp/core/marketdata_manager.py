import os
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import datetime as dt
import glob
import traceback
import math
import ntpath
import shutil

import fanyuanapp.core.constants as constants

from fanyuanapp import db
from fanyuanapp.models import MarketDataSummery, MarketData, DailyResults
from fanyuanapp.core.yahoo_financedata import get_yahoo_market_data
#from fanyuanapp.core.alpha_financedata import alpha_stock
from fanyuanapp import logger

INDEX_SYMBOLS = ['^GSPC', '^DJI', '^IXIC', 'HKHSI']

MARKETDATA_COLUMN_NAMES = [constants.OPEN_COLUMN, constants.HIGH_COLUMN, constants.LOW_COLUMN, constants.CLOSE_COLUMN, constants.VOLUME_COLUMN]

INPUT_DATE_FORMAT = '%m/%d/%Y'

HK_INPUT_DATE_FORMAT = '%Y/%m/%d'

class MarketDataManager:
    
    def __init__(self):
        self.marketDatas = dict()
        self.businessdays = set()

    # def upload_marketdata(self, summery):
    #     ticker = summery.symbol
    #     filename = '{}/{}.csv'.format(constants.MARKETDATA_FOLDER, ticker)
    #     return self.load_marketdata_from_file(filename, summery)


    # def load_marketdata_from_file(self, filename, summery):
    #     ticker = summery.symbol
    #     if os.path.exists(filename):
    #         fromdate = summery.fromdate
    #         todate = summery.todate
    #
    #         marketData = pd.read_csv(filename)
    #         firstrow = True
    #         for row_index, row in marketData.iterrows():
    #             currentDate = row[constants.DATE_COLUMN]
    #             if firstrow:
    #                 start = currentDate
    #                 firstrow = False
    #             end = currentDate
    #
    #             if (fromdate == None or fromdate>currentDate or  currentDate>todate):
    #                 markedata = MarketData(date=row[constants.DATE_COLUMN], symbol=ticker, openprice=row[constants.OPEN_COLUMN], highprice=row[constants.HIGH_COLUMN], lowprice=row[constants.LOW_COLUMN], closeprice=row[constants.CLOSE_COLUMN], volumn=row[constants.VOLUME_COLUMN], summery_id=summery.id)
    #                 db.session.add(markedata)
    #
    #         if fromdate == None or fromdate>start:
    #             summery.fromdate=start
    #         if todate == None or todate<end:
    #             summery.todate=end
    #
    #         db.session.commit()
    #         return True
    #
    #     return False

    def upload_all_stocks_from_file(self, filename):
        full_filename = f'{constants.USERINPUT_FOLDER}/{filename}'
        if os.path.exists(full_filename):
            try:
                lastticker = None
                marketData = pd.read_csv(full_filename)
                for row_index, row in marketData.iterrows():
                    ticker = row[constants.SYMBOL_COLUMN]
                    currentDate = row[constants.DATE_COLUMN]
                    if ticker != lastticker:
                        if lastticker:
                            db.session.commit()
                        lastticker = ticker
                        summery = MarketDataSummery(symbol=ticker)
                        db.session.add(summery)
                        db.session.commit()
                        lastsummery = MarketDataSummery.query.filter_by(symbol=ticker).first()
                        lastsummery.fromdate = currentDate

                    summery.todate = currentDate
                    markedata = MarketData(date=row[constants.DATE_COLUMN], symbol=ticker, openprice=row[constants.OPEN_COLUMN], highprice=row[constants.HIGH_COLUMN], lowprice=row[constants.LOW_COLUMN], closeprice=row[constants.CLOSE_COLUMN], volumn=row[constants.VOLUME_COLUMN], summery_id=summery.id)
                    db.session.add(markedata)

                db.session.commit()
                return True
            except Exception:
                print("Exception for upload_all_stocks_from_file ")
                logger.exception(f'Exceptiion for upload_all_stocks_from_file')
                traceback.print_exc()

        return False

    def download_upload_marketdata(self, filename, start, end):
        print('\n\nDownload market data from {} to {}'.format(start, end))

        full_filename = f'{constants.USERINPUT_FOLDER}/{filename}'
        input = pd.read_csv(full_filename)
        tickers = set(input['Symbol'])

        self.query_upload_marketdata(tickers, start, end)

        self.download_upload_indexes(start, end)

    def query_upload_marketdata(self, tickers, start, end):
        try:
            fromdate = f"{start}"
            todate = f"{end}"
            if end == None:
                todate = dt.datetime.now().strftime(constants.DATE_FORMAT)

            if not os.path.exists('stock_dfs'):
                os.makedirs('stock_dfs')
            total=0
            for ticker in tickers:
                total += 1
                print('{}. {}'.format(total, ticker))
                summery = MarketDataSummery.query.filter_by(symbol=ticker).first()
                if summery == None:
                    summery = MarketDataSummery(symbol=ticker)
                    db.session.add(summery)
                    db.session.commit()
                    summery = MarketDataSummery.query.filter_by(symbol=ticker).first()

                if summery.fromdate == None or fromdate < summery.fromdate or todate > summery.todate:
                    alpha_stock(ticker)
                    # get_yahoo_market_data(ticker, fromdate, todate)
                    self.upload_marketdata(summery)
        except Exception:
            print("Exception for initialing ")
            logger.exception(f'Exceptiion for initialing test')
            traceback.print_exc()
        print('\n\nTotal downloaded market data symbols is {}'.format(total))

    def download_marketdata(self, ticker, fromdate, todate):

        return get_yahoo_market_data(ticker, fromdate, todate)


    def download_upload_indexes(self, start, end):
        print(f'Download all the benchmarks.')
        for i in range(3):
            self.query_upload_marketdata(INDEX_SYMBOLS, start, end)
            getall = True
            for symbol in INDEX_SYMBOLS:
                filename = '{}/{}.csv'.format(constants.MARKETDATA_FOLDER, symbol)
                if not os.path.exists(filename):
                    getall = False;
            if getall:
                break

    def redownload_failed_marketdata(self):
        summeryForDate = MarketDataSummery.query.order_by(MarketDataSummery.fromdate).filter(MarketDataSummery.fromdate != None).first()
        fromdate = None
        if summeryForDate:
            fromdate = summeryForDate.fromdate
        if fromdate == None:
            print('Cannot reload market data because of no fromdate from DB')

        summeryForDate1 = MarketDataSummery.query.order_by(MarketDataSummery.todate.desc()).filter(MarketDataSummery.todate != None).first()
        todate = None
        if summeryForDate:
            todate = summeryForDate1.todate
        if todate == None:
            print('Cannot reload market data because of no todate from DB')

        loadedsummeries = []
        summeries = MarketDataSummery.query.order_by(MarketDataSummery.symbol).filter(MarketDataSummery.fromdate == None).all()
        total=0
        for summery in summeries:
            ticker = summery.symbol
            # print(total, ': ', ticker)
            total += 1
            alpha_stock(ticker)
            # get_yahoo_market_data(ticker, fromdate, todate)
            if self.upload_marketdata(summery):
                loadedsummeries.append(summery)
        return total

    # def get_alpha_marketdata(self, summeries):
    #     numloaded = 0
    #     for summery in summeries:
    #         if summery.fromdate == None:
    #             ticker = summery.symbol
    #             loaded = alpha_stock(ticker)
    #             if loaded:
    #                 numloaded += 1
    #                 upload_marketdata(summery)
    #     return numloaded

    # def load_market_data(self, tickers, startdate, enddate):
    #     self.marketDatas.clear()
    #
    #     startdelta = dt.timedelta(days=1)
    #     if type(enddate) is str:
    #         date = dt.datetime.strptime(startdate, constants.DATE_FORMAT) - startdelta
    #     else:
    #         date = startdate - startdelta
    #     fromdate = date.strftime(constants.DATE_FORMAT)
    #
    #     enddelta = dt.timedelta(days=30)
    #     if type(enddate) is str:
    #         date1 = dt.datetime.strptime(enddate, constants.DATE_FORMAT) + enddelta
    #     else:
    #         date1 = enddate + enddelta
    #     todate = date1.strftime(constants.DATE_FORMAT)
    #
    #     for ticker in tickers:
    #         marketData = self.query_market_data(ticker, fromdate, todate)
    #         if marketData.empty:
    #             print(f"No MarketData available for ticker {ticker}")
    #         else:
    #             self.marketDatas[ticker] = marketData
    #
    #     if not self.marketDatas:
    #         print(f"Not MarketData available for all tickers {tickers}. Please download those marketdata!!!")
    #         return False
    #
    #     return True

    def load_business_days(self, start, end, isHongkongMarket=False):
        self.businessdays.clear()

        if isHongkongMarket:
            ticker = 'HKHSI'
        else:
            ticker = '^GSPC'
        print(f'load_business_days with ticker {ticker}')
        filename = '{}/{}.csv'.format(constants.MARKETDATA_FOLDER, ticker)
        marketData = pd.read_csv(filename)
        if marketData.empty:
            print(f"No MarketData available for S&P from {start} to {end}")
        else:
            for row_index, row in marketData.iterrows():
                dateStr = row[constants.DATE_COLUMN]
                if dateStr >= start and dateStr <= end:
                    self.businessdays.add(dateStr)
            if len(self.businessdays)>0:
                print("Total Business days:", len(self.businessdays))
            else:
                err_str = f'No business days between {start} and {end}'
                print(err_str)
                logger.info(err_str)

    def is_business_day(self, day):
        return len(self.businessdays) == 0 or day in self.businessdays

    def get_market_data(self, ticker, startDate, endDate, asyncDate=True):
        data = self.marketDatas.get(ticker)
        if type(data) is not pd.core.frame.DataFrame:
            print(f"No {ticker} marketdata in cach!")
            return pd.DataFrame()

        startDateStr = startDate.strftime(constants.DATE_FORMAT)
        endDateStr = endDate.strftime(constants.DATE_FORMAT)

        queryData = data.query(f'Date>="{startDateStr}" & Date<="{endDateStr}"')
        if queryData.empty:
            queryData = data.query(f'Date<="{endDateStr}"')
        if asyncDate:
            return queryData
        else:
            return queryData.sort_values([constants.DATE_COLUMN], ascending=False)

    def get_market_data_from(self, ticker, buyDate, holdingDays):
        finalday = int(holdingDays) + (int(holdingDays)/5 + 2)*2
        lastDate = buyDate + dt.timedelta(days=int(finalday))
        present = dt.datetime.now()
        if present < lastDate:
            lastDate = present

        return self.get_market_data(ticker, buyDate, lastDate)

    def previous_min_total_trade(self, ticker, buyDate, minVolPercent):
        startDate = buyDate - dt.timedelta(days=6)
        endDate = buyDate - dt.timedelta(days=1)
        data = self.get_market_data(ticker, startDate, endDate, False)
        if data.empty:
            log_info = f'No Market Data before {buyDate} for {ticker}'
            print(log_info)
            return 0

        firstRow = data.head(1)
        closePrice = float(firstRow[constants.CLOSE_COLUMN])
        volume = firstRow.get(constants.VOLUME_COLUMN).values[0]
        minVolume = (int(volume*float(minVolPercent)))

        return closePrice*minVolume

    def get_previous_trade_date(self, ticker, currentDateStr):
        marketData = self.marketDatas[ticker]

        early8Date = dt.datetime.strptime(currentDateStr, constants.DATE_FORMAT) - dt.timedelta(days=8)
        early8DateStr = early8Date.strftime(constants.DATE_FORMAT)
        subsetMarketData = marketData.query(f'Date>="{early8DateStr}" & Date<"{currentDateStr}"')

        if subsetMarketData.empty:
            print(f'get_previous_trade_date for {ticker}/{currentDateStr}: not found!')
            return None

        return subsetMarketData.tail(1)[constants.DATE_COLUMN].values[0]

    def query_market_data(self, ticker, startdate, enddate):
        queryMarketDatas = pd.DataFrame()
        queryDBResults = MarketData.query.order_by(MarketData.date).filter(MarketData.symbol==ticker, MarketData.date>=startdate, MarketData.date<=enddate).all()
        for row in queryDBResults:
            marketdata = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
            marketdata[constants.DATE_COLUMN] = row.date
            marketdata[constants.SYMBOL_COLUMN] = row.symbol
            marketdata[constants.OPEN_COLUMN] = row.openprice
            marketdata[constants.HIGH_COLUMN] = row.highprice
            marketdata[constants.LOW_COLUMN] = row.lowprice
            marketdata[constants.CLOSE_COLUMN] = row.closeprice
            marketdata[constants.VOLUME_COLUMN] = row.volumn
            if queryMarketDatas.empty:
                queryMarketDatas = marketdata
            else:
                queryMarketDatas = queryMarketDatas.append(marketdata)

        if queryMarketDatas.empty:
            err_str = f'Failed to get {ticker} market data in DB from {startdate} to {enddate}'
            print(err_str)
            logger.info(err_str)

        return queryMarketDatas

    def is_marketdata_available(self, ticker):
        data = self.marketDatas.get(ticker)
        return type(data) is pd.core.frame.DataFrame

    # def upload_all_marketdata(self):
    #     succ = False
    #     try:
    #         datapath = os.path.join(constants.MARKETDATA_FOLDER, "*.csv")
    #         print(datapath)
    #
    #         names = glob.glob(datapath)
    #         # print(names[0])
    #
    #         for name in names:
    #             parts = name.split('.')
    #             strlen = len(parts[0])
    #             if parts[0].find("/"):
    #                 pos = parts[0].index('/')
    #             else:
    #                 pos = parts[0].index('\\')
    #             ticker = parts[0][pos+1:strlen]
    #             # print(ticker)
    #             summery = MarketDataSummery.query.filter_by(symbol=ticker).first()
    #             if summery == None:
    #                 summery = MarketDataSummery(symbol=ticker)
    #                 db.session.add(summery)
    #                 db.session.commit()
    #                 summery = MarketDataSummery.query.filter_by(symbol=ticker).first()
    #                 self.load_marketdata_from_file(name, summery)
    #                 succ = True
    #
    #     except Exception:
    #         print("Exception for initialing ")
    #         logger.exception(f'Exceptiion for initialing test')
    #         traceback.print_exc()
    #         succ = False
    #
    #     print("Finished to upload marketdata")
    #
    #     return succ

    def query_backtest_returns(self, summery_id):
        results = DailyResults.query.filter_by(summery_id=summery_id).all()
        return list(map(lambda res: float(res.returns), results))

    def get_index_return(self, ticker, fromdate, todate):
        # print(f'get_index_return: {ticker} from {fromdate} to {todate}')
        marketData = self.marketDatas[ticker]

        price_data = marketData.query(f'Date>="{fromdate}" & Date<="{todate}"')

        price_data.set_index(constants.DATE_COLUMN, inplace=True)

        price_data = price_data['Close']

        firstdayprice = price_data.head(1).values[0]

        # ret_data = price_data.pct_change()[1:]
        ret_data = pd.Series()
        for index, value in price_data.items():
            newvalue = (value - firstdayprice)/firstdayprice
            ret_data[index] = round(newvalue, 5)

        return ret_data[1:]

    def get_benchmark_pct_change(self, ticker, fromdate, todate):

        marketData = self.marketDatas[ticker]

        price_data = marketData.query(f'Date>="{fromdate}" & Date<="{todate}"')

        price_data.set_index(constants.DATE_COLUMN, inplace=True)

        price_data = price_data['Close']

        ret_data = price_data.pct_change()[1:]

        return ret_data

    def load_benchmark_from_stock_dfs(self):
        for ticker in INDEX_SYMBOLS:
            summery = MarketDataSummery.query.filter_by(symbol=ticker).first()
            if summery == None:
                summery = MarketDataSummery(symbol=ticker)
                db.session.add(summery)
                db.session.commit()
                summery = MarketDataSummery.query.filter_by(symbol=ticker).first()

            if not self.upload_marketdata(summery):
                return False

        return True

    def load_benchmarks_from_stock_dfs(self):
        for idx, ticker in enumerate(INDEX_SYMBOLS):
            filename = f'{constants.MARKETDATA_FOLDER}/{ticker}.csv'
            if os.path.exists(filename):
                marketData = pd.read_csv(filename)

                self.marketDatas[ticker] = marketData
            else:
                print(f'{filename} not found')

    def load_market_data_from_stock_dfs(self, tickers, startdate, enddate):

        self.marketDatas.clear()

        startdelta = dt.timedelta(days=7)
        if type(startdate) is str:
            date = dt.datetime.strptime(startdate, constants.DATE_FORMAT) - startdelta
        else:
            date = startdate - startdelta
        fromdate = date.strftime(constants.DATE_FORMAT)

        todate = enddate

        # if not self.load_benchmark_from_stock_dfs():
        #     print(f'Not all the benchmark files in the folder stock_dfs')
        #     self.download_upload_indexes(fromdate, todate)


        for idx, ticker in enumerate(tickers):
            filename = f'{constants.MARKETDATA_FOLDER}/{ticker}.csv'

            # print(f'{idx}. {filename}')
            if os.path.exists(filename):
                tickerMarketData = pd.read_csv(filename)

                marketData = tickerMarketData.query(f'Date>="{fromdate}" & Date<="{todate}"')

                self.marketDatas[ticker] = marketData

            # else:
            #     info_str = f'{filename} not found'
            #     print(info_str)
            #     logger.info(info_str)

        self.load_benchmarks_from_stock_dfs()

        return True

    def is_valid_market_data(self, row):
        for name in MARKETDATA_COLUMN_NAMES:
            if math.isnan(row[name]):
                return False
        return True

    def save_marketdata(self, ticker, ticker_marketdata, startDate, endDate):
        filename = f'{constants.MARKETDATA_FOLDER}/{ticker}.csv'
        if not os.path.exists(filename):
            ticker_marketdata.to_csv(filename, index=False)
        else: # else it exists so append without writing the header
            ticker_marketdata.to_csv(filename, mode='a', header=False, index=False)
        summery = MarketDataSummery.query.filter_by(symbol=ticker).first()
        if summery == None:
            summery = MarketDataSummery(symbol=ticker, fromdate=startDate, todate=endDate)
            db.session.add(summery)
        else:
            if summery.fromdate == None or startDate < summery.fromdate:
                summery.fromdate = startDate
            if summery.todate == None or endDate > summery.todate:
                summery.todate = endDate
        db.session.commit()

    def get_marketdata_from_file(self, filename):
        full_filename = f'{constants.USERINPUT_FOLDER}/{filename}'
        if os.path.exists(full_filename):
            try:
                lastticker = None
                all_marketData = pd.read_csv(full_filename)
                ticker_marketdata = pd.DataFrame()
                startDate = None
                endDate = None
                for row_index, row in all_marketData.iterrows():
                    ticker = row[constants.SYMBOL_COLUMN]
                    inputDateStr = row[constants.DATE_COLUMN]
                    outputDate = inputDateStr
                    if inputDateStr.find("/")>0:
                        inputdate = dt.datetime.strptime(inputDateStr, INPUT_DATE_FORMAT)
                        outputDate = inputdate.strftime(constants.DATE_FORMAT)

                    if ticker != lastticker:
                        if not ticker_marketdata.empty:
                            self.save_marketdata(lastticker, ticker_marketdata, startDate, endDate)
                            ticker_marketdata = pd.DataFrame()
                        startDate = outputDate
                        lastticker = ticker

                    endDate = outputDate

                    if self.is_valid_market_data(row):
                        marketdata = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
                        marketdata[constants.DATE_COLUMN] = outputDate
                        marketdata[constants.OPEN_COLUMN] = row[constants.OPEN_COLUMN]
                        marketdata[constants.HIGH_COLUMN] = row[constants.HIGH_COLUMN]
                        marketdata[constants.LOW_COLUMN] = row[constants.LOW_COLUMN]
                        marketdata[constants.CLOSE_COLUMN] = row[constants.CLOSE_COLUMN]
                        marketdata[constants.VOLUME_COLUMN] = row[constants.VOLUME_COLUMN]

                        if ticker_marketdata.empty:
                            ticker_marketdata = marketdata
                        else:
                            ticker_marketdata = ticker_marketdata.append(marketdata)

                if not ticker_marketdata.empty:
                    self.save_marketdata(lastticker, ticker_marketdata, startDate, endDate)

                return True

            except Exception:
                print("Exception for upload_all_stocks_from_file ")
                traceback.print_exc()
                return False
        else:
            print(f'file {full_filename} not found')
            return False

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def update_marketdata_summery(self):
        print('Start to create or update market data summeries')
        lastTicker = None
        total = 0
        try:
            datapath = os.path.join(constants.MARKETDATA_FOLDER, "*.csv")

            names = glob.glob(datapath)

            for index, name in enumerate(names, start=1):
                total = index
                if (index % 500) == 0:
                    print(f'Create or update {index} summeries')
                parts = name.split('.')
                ticker = self.path_leaf(parts[0])
                lastTicker = ticker
                # print(ticker)
                summery = MarketDataSummery.query.filter_by(symbol=ticker).first()
                marketData = pd.read_csv(name)
                start = marketData.head(1)[constants.DATE_COLUMN].values[0]
                end = marketData.tail(1)[constants.DATE_COLUMN].values[0]
                if summery == None:
                    summery = MarketDataSummery(symbol=ticker, fromdate=start, todate=end)
                    db.session.add(summery)
                else:
                    summery.fromdate=start
                    summery.todate=end
                db.session.commit()
            print(f'Finished to create or update {total} summeries')
            return True

        except Exception:
            err_msg = f'Exceptiion for creating or update {lastTicker}'
            print(err_msg)
            logger.exception(err_msg)
            traceback.print_exc()

        print("Finished to update marketdata summeries")

        return False

    def upload_marketdata_from_file(self, ticker):
        filename = '{}/{}.csv'.format(constants.MARKETDATA_FOLDER, ticker)
        marketData = pd.read_csv(filename)
        data_list = []
        for index, row in marketData.iterrows():
            data = MarketData(date=row[constants.DATE_COLUMN], symbol=ticker, openprice=row[constants.OPEN_COLUMN], highprice=row[constants.HIGH_COLUMN], lowprice=row[constants.LOW_COLUMN], closeprice=row[constants.CLOSE_COLUMN], volumn=row[constants.VOLUME_COLUMN], summery_id=0)
            data_list.append(data)
        return data_list

    def query_daily_buyinfo(self, summery_id):
        results = DailyResults.query.filter_by(summery_id=summery_id).all()
        days = list(map(lambda res: res.date, results))
        boughtstocks = list(map(lambda res: float(res.boughtstocks), results))
        return (days, boughtstocks)

    def resolve_hk_ticker(self, symbol):
        startPos = symbol.index('(') + 1
        endPos = symbol.index(')')
        ticker_num = symbol[startPos:endPos]
        return f'HK{ticker_num}'

    def get_hk_marketdata_from_file(self, filename):
        full_filename = f'{constants.USERINPUT_FOLDER}/{filename}'
        print(f'start to process {full_filename}')
        if os.path.exists(full_filename):
            try:
                lastticker = None
                all_marketData = pd.read_csv(full_filename, encoding="GBK")
                ticker_marketdata = pd.DataFrame()
                startDate = None
                endDate = None
                for row_index, row in all_marketData.iterrows():
                    ticker = self.resolve_hk_ticker(row[constants.SYMBOL_COLUMN])
                    inputDateStr = row[constants.DATE_COLUMN]
                    outputDate = inputDateStr
                    if inputDateStr.find("/")>0:
                        inputdate = dt.datetime.strptime(inputDateStr, HK_INPUT_DATE_FORMAT)
                        outputDate = inputdate.strftime(constants.DATE_FORMAT)

                    if ticker != lastticker:
                        if not ticker_marketdata.empty:
                            print(f'Save {lastticker}')
                            self.save_marketdata(lastticker, ticker_marketdata, startDate, endDate)
                            ticker_marketdata = pd.DataFrame()
                        startDate = outputDate
                        lastticker = ticker

                    endDate = outputDate

                    if self.is_valid_market_data(row):
                        marketdata = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
                        marketdata[constants.DATE_COLUMN] = outputDate
                        marketdata[constants.OPEN_COLUMN] = row[constants.OPEN_COLUMN]
                        marketdata[constants.HIGH_COLUMN] = row[constants.HIGH_COLUMN]
                        marketdata[constants.LOW_COLUMN] = row[constants.LOW_COLUMN]
                        marketdata[constants.CLOSE_COLUMN] = row[constants.CLOSE_COLUMN]
                        marketdata[constants.VOLUME_COLUMN] = row[constants.VOLUME_COLUMN]

                        if ticker_marketdata.empty:
                            ticker_marketdata = marketdata
                        else:
                            ticker_marketdata = ticker_marketdata.append(marketdata)

                if not ticker_marketdata.empty:
                    print(f'Save {lastticker}')
                    self.save_marketdata(lastticker, ticker_marketdata, startDate, endDate)

                return True

            except Exception:
                print("Exception for upload_all_stocks_from_file ")
                traceback.print_exc()
                return False
        else:
            print(f'file {full_filename} not found')
            return False

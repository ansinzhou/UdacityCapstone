import pandas as pd
import datetime as dt
pd.core.common.is_list_like = pd.api.types.is_list_like
import math
import os
import glob
import traceback

import fanyuanapp.core.constants as constants

from fanyuanapp import db
from fanyuanapp.models import Indicator, BuyInfo, SellInfo
from fanyuanapp import logger


INPUT_DATE_FORMAT = '%m/%d/%Y'
HK_INPUT_DATE_FORMAT = '%Y/%m/%d'

def resolve_hk_symbol(symbol):
    startPos = symbol.index('(') + 1
    endPos = symbol.index(')')
    ticker_num = symbol[startPos:endPos]
    return f'HK{ticker_num}'

def load_buy_indicator(indicator_id, inputFile, hk_stocks):
    log_info = f'Start to upload buy indicator with {inputFile}'
    print(log_info)
    logger.info(log_info)
    try:
        filename = f'{constants.USERINPUT_FOLDER}/{inputFile}'
        if hk_stocks:
            input = pd.read_csv(filename, encoding="GBK")
        else:
            input = pd.read_csv(filename)
        column_names = list(input.columns)
        for row_index, row in input.iterrows():
            symbol = row[constants.SYMBOL_COLUMN]
            if hk_stocks:
                symbol = resolve_hk_symbol(symbol)
            inputDateStr = row[constants.DATE_COLUMN]
            dbDate = inputDateStr
            if inputDateStr.find("/") > 0:
                if hk_stocks:
                    buydate = dt.datetime.strptime(inputDateStr, HK_INPUT_DATE_FORMAT)
                else:
                    buydate = dt.datetime.strptime(inputDateStr, INPUT_DATE_FORMAT)
                dbDate = buydate.strftime(constants.DATE_FORMAT)
            buyprice = row[constants.BUYPRICE_COLUMN]
            if constants.OPEN_COLUMN in column_names:
                openprice = row[constants.OPEN_COLUMN]
            else:
                openprice = 0
            if constants.CLOSE_COLUMN in column_names:
                closeprice = row[constants.CLOSE_COLUMN]
            else:
                closeprice = 0
            if constants.HIGH_COLUMN in column_names:
                highprice = row[constants.HIGH_COLUMN]
            else:
                highprice = 0
            if constants.LOW_COLUMN in column_names:
                lowprice = row[constants.LOW_COLUMN]
            else:
                lowprice = 0
            buy_info = BuyInfo.query.filter(BuyInfo.indicator_id==indicator_id, BuyInfo.symbol==symbol, BuyInfo.buydate==dbDate).first()
            if (not buy_info and math.isnan(float(buyprice)) == False and buyprice > 0.0001):
                buyinfo = BuyInfo(buydate=dbDate, symbol=symbol, buyprice=buyprice, openprice=openprice, closeprice=closeprice, highprice=highprice, lowprice=lowprice, indicator_id=indicator_id)
                db.session.add(buyinfo)

        db.session.commit()
        logger.info('Finish to upload buy indicator')

    except Exception:
        print("Exception for initialing ")
        logger.exception(f'Exceptiion for initialing test')
        traceback.print_exc()

    # allinfo = BuyInfo.query.all()
    # print("All_Info=", allinfo)

def load_sell_indicator(indicator_id, inputFile):
    log_info = f'Start to upload sell indicator with {inputFile}'
    print(log_info)
    logger.info(log_info)

    try:
        filename = f'{constants.USERINPUT_FOLDER}/{inputFile}'
        input = pd.read_csv(filename)
        for row_index, row in input.iterrows():
            symbol = row[constants.SYMBOL_COLUMN]
            inputDateStr = row[constants.DATE_COLUMN]
            dbDate = inputDateStr
            if inputDateStr.find("/")>0:
                selldate = dt.datetime.strptime(inputDateStr, INPUT_DATE_FORMAT)
                dbDate = selldate.strftime(constants.DATE_FORMAT)
            sellprice = row[constants.SELLPRICE_COLUMN]
            sell_info = SellInfo.query.filter(SellInfo.indicator_id==indicator_id, SellInfo.symbol==symbol, SellInfo.selldate==dbDate).first()
            if not sell_info and math.isnan(float(sellprice)) == False and sellprice > 0.0001:
                sellinfo = SellInfo(selldate=dbDate, symbol=symbol, sellprice=sellprice, indicator_id=indicator_id)
                db.session.add(sellinfo)
        db.session.commit()
        logger.info('Finish to upload sell indicator')

    except Exception:
        print("Exception for initialing ")
        logger.exception(f'Exceptiion for initialing test')
        traceback.print_exc()

def load_buy_info(indicator_id):
    datapath = os.path.join(constants.BUYINFO_FOLDER, "*.CSV")
    print(datapath)

    names = glob.glob(datapath)
    print(names)

    for name in names:
        parts = name.split('.')
        strlen = len(parts[0])
        pos = parts[0].index('/')
        if pos == 0:
            pos = parts[0].index('\\')
        ticker = parts[0][pos+1:strlen]
        print(ticker)
        buydata = pd.read_csv(name, encoding='GB18030')
        cleandata = buydata.copy()
        cleandata.columns = ['Date', 'yi', 'er', 'san', 'si', 'wu', 'BuyFlag', 'BuyPrice']
        cleandata['Symbol'] = ticker
        cleandata.drop(['yi', 'er', 'san', 'si', 'wu'], axis=1, inplace=True)
        cleandata = cleandata[['Symbol', 'Date', 'BuyFlag', 'BuyPrice']]
        cleandata.dropna()
        cleandata = cleandata.loc[cleandata['BuyFlag'] == '1']
        cleandata['Date'] = pd.to_datetime(cleandata['Date'], format='%Y-%m-%d')
        cleandata.BuyFlag = pd.to_numeric(cleandata.BuyFlag)
        cleandata.BuyPrice = pd.to_numeric(cleandata.BuyPrice)
        print(cleandata.head())


        for row_index, row in cleandata.iterrows():
            symbol = row[constants.SYMBOL_COLUMN]
            inputDateStr = row['Date']
            dbDate = inputDateStr.strftime(constants.DATE_FORMAT)
            buyprice = row[constants.BUYPRICE_COLUMN]
            openprice = 0
            closeprice = 0
            highprice = 0
            lowprice = 0
            buy_info = BuyInfo.query.filter(BuyInfo.indicator_id==indicator_id, BuyInfo.symbol==symbol, BuyInfo.buydate==dbDate).first()
            if (not buy_info and math.isnan(float(buyprice)) == False and buyprice > 0.0001):
                buyinfo = BuyInfo(buydate=dbDate, symbol=symbol, buyprice=buyprice, openprice=openprice, closeprice=closeprice, highprice=highprice, lowprice=lowprice, indicator_id=indicator_id)
                db.session.add(buyinfo)

        db.session.commit()

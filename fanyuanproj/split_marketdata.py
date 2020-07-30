import os
import datetime as dt
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import traceback
import math

import fanyuanapp.core.constants as constants

INPUT_DATE_FORMAT = '%m/%d/%Y'

market_column_names = [constants.OPEN_COLUMN, constants.HIGH_COLUMN, constants.LOW_COLUMN, constants.CLOSE_COLUMN, constants.VOLUME_COLUMN]

def is_valid_market_data(row):
    for name in market_column_names:
        if math.isnan(row[name]):
            return False
    return True

def upload_all_stocks_from_file(filename):
    full_filename = f'{constants.USERINPUT_FOLDER}/{filename}'
    if os.path.exists(full_filename):
        try:
            lastticker = None
            all_marketData = pd.read_csv(full_filename)
            ticker_marketdata = pd.DataFrame()
            for row_index, row in all_marketData.iterrows():
                ticker = row[constants.SYMBOL_COLUMN]
                if ticker != lastticker:
                    if not ticker_marketdata.empty:
                        print(f'Save {lastticker} data in {filename}')
                        if not os.path.exists(filename):
                            ticker_marketdata.to_csv(filename, index=False)
                        else: # else it exists so append without writing the header
                            ticker_marketdata.to_csv(filename, mode='a', header=False, index=False)
                        ticker_marketdata = pd.DataFrame()
                    lastticker = ticker
                    filename = f'{constants.MARKETDATA_FOLDER}/{lastticker}.csv'


                inputDateStr = row[constants.DATE_COLUMN]
                outputDate = inputDateStr
                if inputDateStr.find("/")>0:
                    inputdate = dt.datetime.strptime(inputDateStr, INPUT_DATE_FORMAT)
                    outputDate = inputdate.strftime(constants.DATE_FORMAT)

                if is_valid_market_data(row):
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
                print(f'Save {lastticker} data in {filename}')
                ticker_marketdata.reset_index()
                if not os.path.exists(filename):
                    ticker_marketdata.to_csv(filename, index=False)
                else: # else it exists so append without writing the header
                    ticker_marketdata.to_csv(filename, mode='a', header=False, index=False)

        except Exception:
            print("Exception for upload_all_stocks_from_file ")
            traceback.print_exc()
    else:
        print(f'file {full_filename} not found')


def upload_stocks_from_files(filenames):
    for filename in filenames:
        upload_all_stocks_from_file(filename)

if __name__ == '__main__':
    if not os.path.exists(constants.MARKETDATA_FOLDER):
        os.makedirs(constants.MARKETDATA_FOLDER)

    # filenames = ['stocks.csv']
    # upload_stocks_from_files(filenames)

    filename ='stocks.csv'
    upload_all_stocks_from_file(filename)
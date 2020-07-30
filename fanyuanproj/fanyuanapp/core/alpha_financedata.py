from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os

ts = TimeSeries(key='AIH485OT2P8QGKIX', output_format = 'pandas')

import fanyuanapp.core.constants as constants

def alpha_stocks(symbols):
    fails = []
    warrants = []
    for symbol in symbols:
        loaded = alpha_stock(symbol)
        if loaded:
            print (symbol + " is a warrant")
            warrants.append(symbol)
        else:
            fails.append(symbol)

def alpha_stock(symbol):
    filename = '{}/{}.csv'.format(constants.MARKETDATA_FOLDER, symbol)
    if os.path.exists(filename):
        print (f'{symbol} has been downloaded before!')
        return False

    succ = True
    print ("Downloading data for " + symbol)
    if '.' in symbol:
        ticker = symbol.split('.')[0]
        try:
            data, meta_data = ts.get_daily_adjusted(symbol = ticker, outputsize='full')
            if data.empty == False:
                data.columns = ['Open','High','Low','Close','Adj Close','Volume','Dividend','Split']
                data.index.names = ['Date']
                data.to_csv(filename)
                succ = True
            else:
                print (f'No data for {symbol}')
                succ = False
        except:
            print (f'{ticker} is not available')
            succ = False
    else:
        print (symbol)
        try:
            data, meta_data = ts.get_daily_adjusted(symbol = symbol, outputsize='full')
            if data.empty == False:
                data.columns = ['Open','High','Low','Close','Adj Close','Volume','Dividend','Split']
                data.index.names = ['Date']

                data.to_csv(filename)
                succ = True
            else:
                print (f'No data for {symbol}')
                succ = False
        except:
            print (f'{symbol} is not available')
            succ = False

    return succ

def find_fails( download, input_all):
    input = pd.read_csv(input_all)
    expected_files = set(input['Symbol'] + '.csv')
    unable_to_download = list(set(expected_files) - set(download))
    return unable_to_download

if __name__ == '__main__':
    inputFile = "TEST2016.csv"
    input = pd.read_csv(inputFile)
    tickers = set(input['Symbol'])
    alpha_stocks(tickers)

    #print(apple_data)
    #alpha_stocks(symbol = ['SOHU'])
    print(tickers)
    print ("The number of stocks is: ")
    print (len(tickers))

    filenames = os.listdir('stock_dfs')
    print (filenames)
    print("The number of downloadable tickers is: ")
    print (len(filenames))
    failed = find_fails(filenames,inputFile)
    if len(failed) > 0:
        print("Failed to download files are: ")
        print (failed)


import pandas as pd

# from fanyuanapp.core.testdata_processor import compile_testdata, load_buyindicators
# import fanyuanapp.core.parameters_util as params
# from fanyuanapp.core.backtest_utils import load_buyindicators, get_indicatrs, save_testsummery
# from fanyuanapp.core.indicator_utils import load_buy_info
#
# from fanyuanapp import db
# from fanyuanapp.models import BuyInfo, TestSummery, TradeActivity, TestStatistics
# # from fanyuanapp.core.yahoo_financedata import get_market_data, get_yahoo_market_data
# # from fanyuanapp.core.alpha_financedata import alpha_stocks
# from fanyuanapp import marketdataManager
# start = '2019-03-27'
# end = '2019-04-05'
# ticker = 'VSTM'

# params.load_buyparameters()
#
# print(params.get_total_cash())
#
# compile_testdata(['2'], [], '2018-11-06', '2018-12-27')


# testsummery = TestSummery(actualtrades=2,
#                           notradesforvolume=0,
#                           notradesforcash=0,
#                           potentialtrades=0,
#                           largestlostsale=0,
#                           totalwins=2,
#                           coverage=0,
#                           maxdailydrawdown=0,
#                           lowestpoint=0)
# db.session.add(testsummery)
# db.session.commit()
# testsummery = TestSummery.query.order_by(TestSummery.date_tested.desc()).first()
# print(testsummery.id)
# testdetails = TestDetails(symbol='ABC',
#                           buydate='2019-10-08',
#                           buyprice=8.8,
#                           volume=100,
#                           saleprice=10.0,
#                           saledate='2019-11-08',
#                           summery_id=testsummery.id)
# db.session.add(testdetails)
# db.session.commit()
# testsummery = TestDetails.query.first()
# print(testdetails)
# firstSum = TestSummery.query.first()
# db.session.delete(firstSum)
# db.session.commit()
# print(TestSummery.query.all())

# print(get_indicatrs(['2']))

# alpha_stocks(['CWEN.A'])

#print(type("aaaa") is str)

# load_buy_info(1)

# buyinfo = BuyInfo.query.filter_by(symbol='AAN').first()
# if buyinfo:
#     print(buyinfo)
#     db.session.delete(buyinfo)
#     db.session.commit()

# upload_marketdata()

# download_upload_indexes(start, end)

# print(get_previous_trade_date('^GSPC', start))
# load_business_days(start, end)
# print(is_business_day(start))
# print(is_business_day('2019-02-08'))
# print(is_business_day('2019-02-09'))
# print(is_business_day('2019-02-18'))

# get_index_return('^GSPC', start, end)
# print(TradeActivity.query.all())
# print(query_market_data(ticker, start, end))
# investedStocks = dict()
# investedStocks['A'] = pd.DataFrame()
# print(investedStocks.get('A'))
# print(investedStocks.get('B'))
#
# print("type=", type(investedStocks.get('A')))
# print("type=", type(investedStocks.get('B')))

# val = None
# print(type(val) is not pd.core.frame.DataFrame)


# class OneLineExceptionFormatter(logging.Formatter):
#     def formatException(self, exc_info):
#         result = super().formatException(exc_info)
#         return repr(result)
#
#     def format(self, record):
#         result = super().format(record)
#         if record.exc_text:
#             result = result.replace("\n", "")
#         return result
#
# handler = logging.StreamHandler()
# formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT)
# handler.setFormatter(formatter)

# logfile =
# print(logfile)
#
#
# def main():
#     root.info("Hello, world")
# try:
#     exit(main())
# except Exception:
#     logging.exception("Exception in main(): ")
#     exit(1)

# d = {u'2012-06-08': 388,
#      u'2012-06-09': 388,
#      u'2012-06-10': 388,
#      u'2012-06-11': 389,
#      u'2012-06-12': 389,
#      u'2012-06-13': 389,
#      u'2012-06-14': 389,
#      u'2012-06-15': 389,
#      u'2012-06-16': 389}
#
# df = pd.DataFrame(list(d.items()), columns=['Date', 'DateValue'])
filename = 'stock_dfs/HK01818.csv'
df = pd.read_csv(filename)
data = df.loc[df['Date']=='2019-10-14']
print(float(data['Close'].values[0]))

# symbol = '                  »ã·á¿Ø¹É (00005)'
# startPos = symbol.index('(') + 1
# endPos = symbol.index(')')
# substr = symbol[startPos:endPos]
# print(substr)
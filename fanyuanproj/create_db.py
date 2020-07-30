import os
from fanyuanapp import db
from fanyuanapp.models import GlobalVariables, IndicatorVariables, Indicator, BuyInfo, SellInfo, MarketDataSummery, MarketData
from fanyuanapp import marketdataManager

db.drop_all()

db.create_all()

globals = GlobalVariables(capital=20_000_000, leverage=0, friction=0)

db.session.add(globals)

db.session.commit()

globals_from_db = GlobalVariables.query.all()


indicator = Indicator(name="Dummy")

db.session.add(indicator)

db.session.commit()

summery = MarketDataSummery(symbol='Dummy')

db.session.add(summery)

db.session.commit()

indicator = Indicator.query.first()

trading_variables = IndicatorVariables(maxstocks=20, maxdays=20, target1=6, target2=10, cutloss=-8, minvolume=5, minbuy=500_000, tradingfee=0.01, maxtradingfee=0.01, indicator_id=indicator.id)

db.session.add(trading_variables)


buyinfo = BuyInfo(buydate="2018-08-18", symbol="DUMMY", buyprice=0, openprice=0, highprice=0, lowprice=0, closeprice=0, indicator_id=indicator.id)

db.session.add(buyinfo)

sellinfo = SellInfo(selldate="2018-08-18", symbol="DUMMY", sellprice=0, indicator_id=indicator.id)

db.session.add(sellinfo)

summery = MarketDataSummery.query.first()

markedata = MarketData(date='2018-08-18', symbol="DUMMY", openprice=0, highprice=0, lowprice=0, closeprice=0, volumn=0, summery_id=summery.id)

db.session.add(markedata)

db.session.commit()

# print("Upload market data")
# marketdataManager.upload_all_marketdata()

print('Done!')

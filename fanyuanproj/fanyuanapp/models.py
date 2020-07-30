from datetime import datetime
from fanyuanapp import db

class GlobalVariables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capital = db.Column(db.Integer,  nullable=False)
    leverage = db.Column(db.Integer,  nullable=False, default=0)
    long_leverage = db.Column(db.Integer,  nullable=False, default=0)
    short_leverage = db.Column(db.Integer,  nullable=False, default=0)
    friction = db.Column(db.Integer,  nullable=False, default=0)

    def __repr__(self):
        return f"GlobalVariable('{self.capital}', '{self.leverage}', '{self.friction}')"

class IndicatorVariables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maxstocks = db.Column(db.Integer, nullable=False)
    maxdays = db.Column(db.Integer,  nullable=False)
    target1 = db.Column(db.Integer,  nullable=False)
    target2 = db.Column(db.Integer,  nullable=False)
    cutloss = db.Column(db.Integer,  nullable=False)
    minvolume = db.Column(db.Integer,  nullable=False)
    minbuy = db.Column(db.Integer,  nullable=False)
    tradingfee = db.Column(db.Float,  nullable=False)
    maxtradingfee = db.Column(db.Float,  nullable=False)
    hongkongmarket = db.Column(db.Integer, default=0)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator.id'), nullable=False)

    def __repr__(self):
        return f"IndicatorVariables({self.maxstocks}, {self.maxdays}, {self.target1}, {self.target2}, {self.cutloss}, {self.minvolume}, {self.minbuy}, {self.tradingfee}, {self.maxtradingfee})"

class Indicator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    buyinputs = db.relationship('BuyInfo', backref='indicator', lazy=True)
    sellinputs = db.relationship('SellInfo', backref='indicator', lazy=True)
    variables = db.relationship('IndicatorVariables', backref='indicator', lazy=True)

    def __repr__(self):
        return f"GlobalVariable('{self.name}')"

class BuyInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buydate = db.Column(db.String(20),  nullable=False)
    symbol = db.Column(db.String(30),  nullable=False)
    buyprice = db.Column(db.Float,  nullable=False, default=0)
    openprice = db.Column(db.Float)
    highprice = db.Column(db.Float)
    lowprice = db.Column(db.Float)
    closeprice = db.Column(db.Float)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator.id'), nullable=False)

    def __repr__(self):
        return f"BuyInfo('{self.buydate}', '{self.symbol}', '{self.buyprice}')"

class SellInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    selldate = db.Column(db.String(20),  nullable=False)
    symbol = db.Column(db.String(30),  nullable=False)
    sellprice = db.Column(db.Float,  nullable=False, default=0)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator.id'), nullable=False)

    def __repr__(self):
        return f"SellInfo('{self.selldate}', '{self.symbol}', '{self.sellprice}')"

class MarketDataSummery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(30), unique=True,  nullable=False)
    fromdate = db.Column(db.String(20))
    todate = db.Column(db.String(20))
    details = db.relationship('MarketData', backref='summery', lazy=True)

    def __repr__(self):
        return f"MarketDataSummery('{self.symbol}', '{self.fromdate}', '{self.todate}')"

class MarketData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(20),  nullable=False)
    openprice = db.Column(db.Float, nullable=False)
    highprice = db.Column(db.Float, nullable=False)
    lowprice = db.Column(db.Float, nullable=False)
    closeprice = db.Column(db.Float, nullable=False)
    volumn = db.Column(db.Integer, nullable=False)
    summery_id = db.Column(db.Integer, db.ForeignKey('market_data_summery.id'), nullable=False)

    def __repr__(self):
        return f"MarketData('{self.symbol}', '{self.date}', '{self.openprice}', '{self.highprice}', '{self.lowprice}', '{self.closeprice}', '{self.volumn}')"

class TestSummery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_tested = db.Column(db.DateTime,  nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(20), nullable=False)
    start = db.Column(db.String(20), nullable=False)
    end = db.Column(db.String(20), nullable=False)
    indicators = db.Column(db.String(50))
    returns = db.Column(db.String(10))
    status = db.Column(db.String(10))
    hongkongmarket = db.Column(db.Integer, default=0)
    statistics = db.relationship('TestStatistics', backref='summery', lazy=True)
    activity = db.relationship('TradeActivity', backref='summery', lazy=True)
    dailyresults = db.relationship('DailyResults', backref='summery', lazy=True)
    dailypositions = db.relationship('DailyPositions', backref='summery', lazy=True)
    failedtrades = db.relationship('FailedTrades', backref='summery', lazy=True)

    def __repr__(self):
        return f"TestSummery('{self.name}', '{self.start}', '{self.end}', '{self.returns}', '{self.status}')"

class TestStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    returns = db.Column(db.String(10))
    beta = db.Column(db.String(10))
    alpha = db.Column(db.String(10))
    sharpe = db.Column(db.String(10))
    trades = db.Column(db.String(10))
    notradesforvolume = db.Column(db.String(10))
    notradesforcash = db.Column(db.String(10))
    potentialtrades = db.Column(db.String(10))
    lostsale = db.Column(db.String(20))
    wins = db.Column(db.String(10))
    loss = db.Column(db.String(10))
    coverage = db.Column(db.String(10))
    drawdown = db.Column(db.String(10))
    lowestpoint = db.Column(db.String(20))
    turnover = db.Column(db.String(10))
    leverage = db.Column(db.String(20))
    cashused = db.Column(db.String(20))
    holdings = db.Column(db.String(10))
    period = db.Column(db.String(10))
    volatility = db.Column(db.String(10))
    summery_id = db.Column(db.Integer, db.ForeignKey('test_summery.id'), nullable=False)

    def __repr__(self):
        return f"TestStatistics('{self.returns}','{self.beta}','{self.alpha}','{self.sharpe}','{self.trades}'," \
               f"'{self.notradesforvolume}','{self.notradesforcash}','{self.potentialtrades}','{self.lostsale}'," \
               f"'{self.wins}','{self.loss}','{self.coverage}', '{self.drawdown}','{self.lowestpoint}','{self.turnover}'," \
               f"'{self.leverage}','{self.cashused}','{self.holdings}','{self.period}','{self.volatility}')"

class TradeActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(20),  nullable=False)
    symbol = db.Column(db.String(30), nullable=False)
    tranaction = db.Column(db.String(10),  nullable=False)
    unitprice = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    summery_id = db.Column(db.Integer, db.ForeignKey('test_summery.id'), nullable=False)

    def __repr__(self):
        return f"TradeActivity('{self.position}', '{self.symbol}', '{self.tranaction}', '{self.unitprice}', '{self.quantity}')"


class DailyResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20),  nullable=False)
    cash = db.Column(db.Integer, nullable=False)
    holding = db.Column(db.Integer, nullable=False)
    actualportfolio = db.Column(db.Integer, nullable=False)
    portfolio = db.Column(db.Integer, nullable=False)
    leverage = db.Column(db.Float, nullable=False)
    drawdown = db.Column(db.Float, nullable=False)
    boughtstocks=db.Column(db.Integer, default=0)
    returns = db.Column(db.Float, nullable=False)
    summery_id = db.Column(db.Integer, db.ForeignKey('test_summery.id'), nullable=False)

    def __repr__(self):
        return f"TestDailyResults({self.tradingdate}, {self.returns}, {self.cash}, {self.holding}, '{self.acutalportfolio}', {self.portfolio}, {self.leverage}, {self.drawdown})"

class DailyPositions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20),  nullable=False)
    symbol = db.Column(db.String(30), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    unitprice = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Float,  nullable=False)
    gainloss = db.Column(db.Float, nullable=False)
    summery_id = db.Column(db.Integer, db.ForeignKey('test_summery.id'), nullable=False)

    def __repr__(self):
        return f"DailyPositions({self.date}, {self.symbol}, {self.unitprice}, {self.quantity}, {self.position}, {self.period}, {self.gainloss})"

class FailedTrades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20),  nullable=False)
    symbol = db.Column(db.String(30), nullable=False)
    reason = db.Column(db.String(20),  nullable=False)
    summery_id = db.Column(db.Integer, db.ForeignKey('test_summery.id'), nullable=False)

    def __repr__(self):
        return f"TradeFailures({self.date}, '{self.symbol}', '{self.type}')"

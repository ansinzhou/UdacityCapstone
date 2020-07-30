class BuyParameters:
    capital = 0
    leverage = 0
    long_leverage = 0
    short_leverage = 0
    friction = 0

    def __init__(self, maxstocks, maxdays, target1, target2, cutloss, minvolume, minbuy, tradingfee, maxtradingfee):
        self.maxstocks = maxstocks
        self.maxdays = maxdays
        self.target1 = target1
        self.target2 = target2
        self.cutloss = cutloss
        self.minvolume = minvolume
        self.minbuy = minbuy
        self.tradingfee = tradingfee
        self.maxtradingfee = maxtradingfee

    def __repr__(self):
        return  f"BuyParameters({BuyParameters.capital},{self.maxstocks},{self.maxdays},{self.target1}," \
                f"{self.target2},{self.cutloss},{self.minvolume},{self.minvolume},{self.tradingfee},{self.maxtradingfee}," \
                f"{BuyParameters.leverage},{BuyParameters.short_leverage},{BuyParameters.friction})"

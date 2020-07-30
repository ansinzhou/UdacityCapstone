from fanyuanapp.models import GlobalVariables, IndicatorVariables

import fanyuanapp.core.constants as constants

from fanyuanapp.core.buy_parameters import BuyParameters

hongkongstock = False

def profit_price1(indicator_id, buyPrice):
    buyParams = get_buyparameters(indicator_id)
    gainPrice = float(buyPrice) + float(buyPrice)*(buyParams.target1/100.0)
    return gainPrice

def profit_price2(indicator_id, buyPrice):
    buyParams = get_buyparameters(indicator_id)
    gainPrice = float(buyPrice) + float(buyPrice)*(buyParams.target2/100.0)
    return gainPrice

def stop_loss_price(indicator_id, buyPrice):
    buyParams = get_buyparameters(indicator_id)
    lossPrice = buyPrice + float(buyPrice)*(buyParams.cutloss/100.0)
    return lossPrice

def invest_money_per_stock(indicator_id, totolAvailableMoney):
    buyParams = get_buyparameters(indicator_id)
    return totolAvailableMoney/buyParams.maxstocks

def get_max_holding_days(indicator_id):
    buyParams = get_buyparameters(indicator_id)
    return buyParams.maxdays

def get_minimum_volumn_percent(indicator_id):
    buyParams = get_buyparameters(indicator_id)
    return buyParams.minvolume/100.0

def get_minimum_buy(indicator_id):
    buyParams = get_buyparameters(indicator_id)
    return buyParams.minbuy

def get_total_cash():
    return BuyParameters.capital

def get_leverage_ratio():
    return BuyParameters.leverage/100.0

def get_long_leverage_ratio():
    return BuyParameters.long_leverage/100.0

def get_short_leverage_ratio():
    return BuyParameters.short_leverage/100.0

def get_leverages(totalCash):
    leverage = totalCash*get_leverage_ratio()
    longleverage = totalCash*get_long_leverage_ratio()
    shortleverage = totalCash*get_short_leverage_ratio()
    return (leverage, longleverage, shortleverage)

def load_buyparameters(indicator_ids):
    mapBuyParameters.clear()
    global hongkongstock

    globals = GlobalVariables.query.first()
    BuyParameters.capital = globals.capital
    BuyParameters.leverage = globals.leverage
    BuyParameters.long_leverage = globals.long_leverage
    BuyParameters.short_leverage = globals.short_leverage
    BuyParameters.friction = globals.friction

    for indicator_id in indicator_ids:
        variables = IndicatorVariables.query.filter_by(indicator_id=indicator_id).first()
        if variables:
            hongkongstock = variables.hongkongmarket>0
            parameters = BuyParameters(variables.maxstocks,variables.maxdays,
                    variables.target1,variables.target2,variables.cutloss,
                    variables.minvolume,variables.minbuy,variables.tradingfee,variables.maxtradingfee)
            mapBuyParameters[int(indicator_id)] = parameters

def get_buyparameters(indicator_id):
    return mapBuyParameters[indicator_id]

def is_short_parameters(indicator_id):
    buyParams = get_buyparameters(indicator_id)
    return buyParams.cutloss>0

def is_hongkong_stock():
    return hongkongstock

# def get_trading_cost(indicator_id, numStocks, totalGainMoney):
#
#     buyParams = get_buyparameters(indicator_id)
#     tradingFeePerStock = buyParams.tradingfee
#     maxTradingFeePerStock = buyParams.maxtradingfee
#     internalFriction = BuyParameters.friction/100.0
#
#     totalCost = float(tradingFeePerStock) * int(numStocks)
#     maxTradingFee = totalGainMoney * float(maxTradingFeePerStock)
#
#     if (totalCost > maxTradingFee):
#         totalCost = maxTradingFee
#
#     totalCost += totalGainMoney * float(internalFriction)
#
#     return totalCost

def buy_stocks(indicator_id, buyPrice, minTradeVolumn, canInvestTotalCapital):
    buyParams = get_buyparameters(indicator_id)
    tradingFeePerStock = buyParams.tradingfee
    maxTradingFeePerStock = buyParams.maxtradingfee
    price = float(buyPrice)
    availableInvestPerStock = invest_money_per_stock(indicator_id, canInvestTotalCapital)
    maxTradingFee = availableInvestPerStock * float(maxTradingFeePerStock)
    minbuy = get_minimum_buy(indicator_id)

    if availableInvestPerStock <= minTradeVolumn:
        num_stocks = int((availableInvestPerStock-maxTradingFee)/price)
        num_stocks1 = int(availableInvestPerStock / (price+tradingFeePerStock))
    elif minTradeVolumn >= minbuy and minTradeVolumn < availableInvestPerStock:
        num_stocks = int((minTradeVolumn-maxTradingFee)/price)
        num_stocks1 = int(minTradeVolumn / (price+tradingFeePerStock))
    else:
        num_stocks = 0
        num_stocks1 = 0

    if num_stocks == 0:
        stocks = 0
        totalInvest = 0
    elif (num_stocks1 >= num_stocks):
        stocks = num_stocks1
        totalInvest = stocks*price + stocks*tradingFeePerStock
    else:
        stocks = num_stocks1
        totalInvest = stocks*price + maxTradingFee

    return (stocks, totalInvest)

def get_sale_price_date(indicator_id, buyPrice, marketData):
    profitPrice1 = profit_price1(indicator_id, buyPrice)
    profitPrice2 = profit_price2(indicator_id, buyPrice)
    stopLossPrice = stop_loss_price(indicator_id, buyPrice)
    salePrice = 0
    saleDate = None

    skipFirstTime = True
    maxholdingdays = get_max_holding_days(indicator_id)

    for row_index, row in marketData.iterrows():

        highPrice = float(row[constants.HIGH_COLUMN])
        lowPrice = float(row[constants.LOW_COLUMN])
        saleDate = row[constants.DATE_COLUMN]
        # print(f'{maxholdingdays}: {saleDate}')
        lastSalePrice = row[constants.CLOSE_COLUMN]
        if (lastSalePrice > 0.0001):
            maxholdingdays -= 1
        else:
            print(f'Hodilday: {saleDate}')

        if highPrice>stopLossPrice and stopLossPrice > lowPrice:
            salePrice = stopLossPrice
            break
        elif highPrice>profitPrice2 and profitPrice2 > lowPrice:
            salePrice = profitPrice2
            break
        elif highPrice>profitPrice1 and profitPrice1 > lowPrice:
            if skipFirstTime:
                skipFirstTime = False
            else:
                salePrice = profitPrice1
                break

        salePrice = lastSalePrice
        if maxholdingdays == 0:
            # print(f'MaxDate: {saleDate}')
            break

    return (saleDate, salePrice)

mapBuyParameters = dict()

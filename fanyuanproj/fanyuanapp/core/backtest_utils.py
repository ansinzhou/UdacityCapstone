import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like

import fanyuanapp.core.constants as constants

import fanyuanapp.core.parameters_util as params

from fanyuanapp.models import Indicator, BuyInfo, SellInfo


def load_buyindicators(indicators, startdate, enddate):
    buyinput = pd.DataFrame()
    for indicator_id in indicators:
        queryDBResults = BuyInfo.query.filter(BuyInfo.indicator_id==indicator_id, BuyInfo.buydate>=startdate, BuyInfo.buydate<=enddate).all()
        for buyinfo in queryDBResults:
            inputdata = pd.DataFrame([1], columns=[constants.DATE_COLUMN])
            inputdata[constants.DATE_COLUMN] = buyinfo.buydate
            inputdata[constants.SYMBOL_COLUMN] = buyinfo.symbol
            inputdata[constants.BUYPRICE_COLUMN] = buyinfo.buyprice
            inputdata[constants.INDICATOR_COLUMN] = buyinfo.indicator_id
            if buyinput.empty:
                buyinput = inputdata
            else:
                buyinput = buyinput.append(inputdata)
    if buyinput.empty:
        print("No buy indicator available!!")
        return buyinput

    return buyinput.sort_values([constants.DATE_COLUMN], ascending=True)

def get_sale_date_with_indicator(indicator_id, ticker, buydate):
    sale_info = SellInfo.query.order_by(SellInfo.selldate).filter(SellInfo.indicator_id==indicator_id, SellInfo.symbol==ticker, SellInfo.selldate>=buydate).first()
    if sale_info:
        return (sale_info.selldate, float(sale_info.sellprice))
    return (None, 0, 0)

def get_indicator_names(indicator_ids):
    ids = []
    for id in indicator_ids:
        ids.append(int(id))
    names = ""
    indicators = Indicator.query.all()
    for indicator in indicators:
        if indicator.id in ids:
            if names == "":
                names = indicator.name
            else:
                names = names + "/" + indicator.name
    return names

def get_sale_price_date(indicator_id, use_sell_indicator, ticker, buyDate, buyPrice, marketData):
    # print("use_sell_indicator=", use_sell_indicator)
    if use_sell_indicator:
        return get_sale_date_with_indicator(indicator_id, ticker, buyDate)
    else:
        return params.get_sale_price_date(indicator_id, buyPrice, marketData)

def get_final_sale_price(isShortProcess, salePrice, buyPrice):
    finalSalePrice = salePrice
    if isShortProcess:
        finalSalePrice = 2*float(buyPrice) - float(salePrice)
    return finalSalePrice
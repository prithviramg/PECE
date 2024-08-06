import datetime as dt
import numpy as np
import kite_trade

kite = kite_trade.KiteApp(enctoken="tpji5yCFp1Pqi+fPtxnsgSjToocIXeurT9Pgs2PgJZoqOL5ji7Q6Z/17BU8/hjswVO3s/GBq1jP+tXfRz0PX2OSPDRUr1Euv59gulFJ9535KdbLWiDukaw==")

def getExpiryDate(week):
    today = dt.datetime.today()
    today = dt.date(today.year, today.month, today.day)
    if week == "NEAR" and today.weekday() <= 3:
            return today + dt.timedelta(3 - today.weekday())
    return today + dt.timedelta(10 - today.weekday())

def getAtmStrike(strikes, expiryDate, nearestStrikeIdx, tradeInstruments):
    min_diff = np.iinfo(np.int16).max
    atmStrike = 0
    retSymbolCE = 0
    retSymbolPE = 0
    mask = tradeInstruments['expiry'] == expiryDate
    mask = mask & (tradeInstruments['segment'] == "NFO-OPT")
    mask = mask & (tradeInstruments['name'] == "NIFTY")
    for idx, eachStrikePrice in enumerate(strikes[nearestStrikeIdx-3 : nearestStrikeIdx+4]):
        strikeSymbolCE, strikeSymbolPE = tradeInstruments[mask & (tradeInstruments['strike'] == eachStrikePrice)]['tradingsymbol'].to_list()
        key_name = "NFO:{}".format(strikeSymbolCE)
        diff = kite.quote(key_name)[key_name]['last_price'] 
        key_name = "NFO:{}".format(strikeSymbolPE)
        diff = abs(diff - kite.quote(key_name)[key_name]['last_price'])
        if min_diff > diff:
            atmStrike = eachStrikePrice
            min_diff = diff
            retSymbolCE = strikeSymbolCE
            retSymbolPE = strikeSymbolPE
    return atmStrike, nearestStrikeIdx-2+idx, retSymbolCE, retSymbolPE
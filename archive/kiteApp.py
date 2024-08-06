import pandas as pd
import datetime as dt
import joblib
import numpy as np
import utils
import time
from utils import kite

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(lineno)d | %(message)s',
    handlers=[
        logging.FileHandler("{}.log".format(dt.date.today().strftime("%Y_%m_%d"))),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()

# logging.basicConfig(format='%(asctime)s %(lineno)d %(message)s')
# logging.getLogger().setLevel(logging.INFO)
# log = logging.getLogger()
# fileHandler = logging.FileHandler("{}.log".format(dt.date.today().strftime("%Y_%m_%d")))
# log.addHandler(fileHandler)
# consoleHandler = logging.StreamHandler()
# log.addHandler(consoleHandler)

instumentsDict = kite.instruments("NFO")
tradeInstruments = pd.DataFrame(instumentsDict)
tradeInstruments['expiry'] = pd.to_datetime(tradeInstruments['expiry'], format="%Y-%m-%d").dt.date
log.info("fetched trade instruments from Zerodha")
strikes = np.arange(start=6000, stop=30000, step=50)

while True:
    if dt.datetime.now().strftime("%H:%M:%S") > "09:25:00":
        break
    else:
        time.sleep(10)
log.info("current time: {} trading started".format(dt.datetime.now().strftime("%H:%M:%S")))
expiryDate = utils.getExpiryDate("NEAR")
log.info("selected expiry date: {}".format(expiryDate))

nifty_curr_spot = kite.quote("NSE:NIFTY 50")['NSE:NIFTY 50']
log.info("current nifty price is {}".format(nifty_curr_spot['last_price']))
python_orders = pd.DataFrame(columns = ['tradingsymbol', 'transaction_type', 'price'])
zerodha_orders = pd.DataFrame(kite.orders())
nearestStrikeIdx = np.searchsorted(strikes, nifty_curr_spot['last_price'])
atmStrike, atmStrikeIdx, strikeSymbolCE, strikeSymbolPE = utils.getAtmStrike(strikes, expiryDate, nearestStrikeIdx, tradeInstruments)
log.info("ATM strike chosen: {} and idx: {}".format(atmStrike, atmStrikeIdx))
log.info("symbols chosen: {} and {}".format(strikeSymbolCE, strikeSymbolPE))
key_name = "NFO:{}".format(strikeSymbolCE)
last_traded_price = kite.ltp(key_name)[key_name]['last_price']
python_orders = python_orders.append({'strikes':str(strikeSymbolCE), 'transaction_type':kite.TRANSACTION_TYPE_SELL, 'price':last_traded_price}, ignore_index = True)
# python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolCE, 
#                                     transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=50, product=kite.PRODUCT_MIS, 
#                                     order_type=kite.ORDER_TYPE_MARKET, tag="_opening_{}".format(strikeSymbolCE)))
log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolCE, kite.TRANSACTION_TYPE_SELL, last_traded_price))
# python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolPE, \
#                                     transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=50, product=kite.PRODUCT_MIS, 
#                                     order_type=kite.ORDER_TYPE_MARKET, tag="_opening_{}".format(strikeSymbolPE)))
key_name = "NFO:{}".format(strikeSymbolPE)
last_traded_price = kite.ltp(key_name)[key_name]['last_price']
python_orders = python_orders.append({'strikes':str(strikeSymbolPE), 'transaction_type':kite.TRANSACTION_TYPE_SELL, 'price':last_traded_price}, ignore_index = True)
log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolPE, kite.TRANSACTION_TYPE_SELL, last_traded_price))
nifty_prev_spot = nifty_curr_spot
while True:
    if dt.datetime.now().strftime("%H:%M:%S") > "15:25:00":
        log.info("--------------------------------------------------------")
        log.info("END OF TODAY'S SESSION, SEE YOU NEXT DAY")
        # mask = zerodha_orders['product'] == "MIS"
        # mask = mask & (zerodha_orders['status'] == "COMPLETE")
        # gain = zerodha_orders[mask & (zerodha_orders['transaction_type'] == "SELL")]['average_price'].sum() 
        # gain = (gain - zerodha_orders[mask & (zerodha_orders['transaction_type'] == "BUY")]['average_price'].sum()) * 50
        gain = python_orders[(python_orders['transaction_type'] == "SELL")]['price'].sum() 
        gain = (gain - python_orders[(python_orders['transaction_type'] == "BUY")]['price'].sum()) * 50
        gain = gain - (len(python_orders)*25)
        log.info("total profit/loss you made today is: {}".format(gain))
        log.info("good buy!!! I hope you had a nice trading day")
        joblib.dump(python_orders, "{}_orders.joblib".format(dt.date.today().strftime("%Y_%m_%d")))
        break
    else:
        nifty_curr_spot = kite.quote("NSE:NIFTY 50")['NSE:NIFTY 50']
        condition1 = nifty_curr_spot['last_price'] > nifty_prev_spot['last_price']
        condition1 = condition1 and (15 <= nifty_curr_spot['last_price'] % 50 <= 25)
        condition2 = ((dt.datetime.now().minute % 5) == 0) and (dt.datetime.now().second < 30)
        condition2 = condition2 and (nifty_curr_spot['last_price'] > nifty_prev_spot['last_price'])
        condition2 = condition2 and (nifty_curr_spot['last_price'] % 50 <= 10)
        if nifty_curr_spot['last_price'] > (nifty_prev_spot['last_price'] + 50):
            log.info("nifty moved up 50 points, current spot is {}".format(nifty_curr_spot['last_price']))
            # python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolCE, 
            #                                     transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=50, product=kite.PRODUCT_MIS, 
            #                                     order_type=kite.ORDER_TYPE_MARKET, tag="python_closing_{}".format(strikeSymbolCE)))
            key_name = "NFO:{}".format(strikeSymbolCE)
            last_traded_price = kite.ltp(key_name)[key_name]['last_price']
            python_orders = python_orders.append({'strikes':str(strikeSymbolCE), 'transaction_type':kite.TRANSACTION_TYPE_BUY, 'price':last_traded_price}, ignore_index = True)
            log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolCE, kite.TRANSACTION_TYPE_BUY, last_traded_price))
            nifty_prev_spot = nifty_curr_spot
            atmStrikeIdx = atmStrikeIdx + 1
            atmStrike, atmStrikeIdx, strikeSymbolCE, strikeSymbolPE = utils.getAtmStrike(strikes, expiryDate, atmStrikeIdx, tradeInstruments)

            # strikeTrades = len(zerodha_orders[zerodha_orders['tradingsymbol'] == strikeSymbolCE])
            strikeTrades = len(python_orders[python_orders['tradingsymbol'] == strikeSymbolCE])
            log.info("no of trades taken for symbol {} in order history is: {}".format(strikeSymbolCE, strikeTrades))
            if (strikeTrades%2) == 0:   # to check if there is 1 buy and 1 sell
                # python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolCE, 
                #                                     transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=50, product=kite.PRODUCT_MIS, 
                #                                     order_type=kite.ORDER_TYPE_MARKET,  tag="python_opening_{}".format(strikeSymbolCE)))
                key_name = "NFO:{}".format(strikeSymbolCE)
                last_traded_price = kite.ltp(key_name)[key_name]['last_price']
                python_orders = python_orders.append({'strikes':str(strikeSymbolCE), 'transaction_type':kite.TRANSACTION_TYPE_SELL, 'price':last_traded_price}, ignore_index = True)
                log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolCE, kite.TRANSACTION_TYPE_SELL, last_traded_price))

            # strikeTrades = len(zerodha_orders[zerodha_orders['tradingsymbol'] == strikeSymbolPE])
            strikeTrades = len(python_orders[python_orders['tradingsymbol'] == strikeSymbolPE])
            log.info("no of trades taken for symbol {} in order history is: {}".format(strikeSymbolPE, strikeTrades))
            if (strikeTrades%2) == 0:   # to check if there is 1 buy and 1 sell
                # python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolPE, 
                #                                     transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=50, product=kite.PRODUCT_MIS, 
                #                                     order_type=kite.ORDER_TYPE_MARKET, tag="python_opening_{}".format(strikeSymbolPE)))
                key_name = "NFO:{}".format(strikeSymbolPE)
                last_traded_price = kite.ltp(key_name)[key_name]['last_price']
                python_orders = python_orders.append({'strikes':str(strikeSymbolPE), 'transaction_type':kite.TRANSACTION_TYPE_SELL, 'price':last_traded_price}, ignore_index = True)
                log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolPE, kite.TRANSACTION_TYPE_SELL, last_traded_price))
        
        elif nifty_curr_spot['last_price'] < (nifty_prev_spot['last_price'] - 50):
            log.info("nifty moved down 50 points, current spot is {}".format(nifty_curr_spot['last_price']))
            # python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolPE, 
            #                                     transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=50, product=kite.PRODUCT_MIS, 
            #                                     order_type=kite.ORDER_TYPE_MARKET, tag="python_closing_{}".format(strikeSymbolPE)))
            nifty_prev_spot = nifty_curr_spot
            key_name = "NFO:{}".format(strikeSymbolPE)
            last_traded_price = kite.ltp(key_name)[key_name]['last_price']
            python_orders = python_orders.append({'strikes':str(strikeSymbolPE), 'transaction_type':kite.TRANSACTION_TYPE_BUY, 'price':last_traded_price}, ignore_index = True)
            log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolPE, kite.TRANSACTION_TYPE_BUY, last_traded_price))
            atmStrikeIdx = atmStrikeIdx - 1
            atmStrike, atmStrikeIdx, strikeSymbolCE, strikeSymbolPE = utils.getAtmStrike(strikes, expiryDate, atmStrikeIdx, tradeInstruments)

            # strikeTrades = len(zerodha_orders[zerodha_orders['tradingsymbol'] == strikeSymbolCE])
            strikeTrades = len(python_orders[python_orders['tradingsymbol'] == strikeSymbolCE])
            log.info("no of trades taken for symbol {} in order history is: {}".format(strikeSymbolCE, strikeTrades))
            if (strikeTrades%2) == 0:   # to check if there is 1 buy and 1 sell
                # python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolCE, 
                #                                     transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=50, product=kite.PRODUCT_MIS, 
                #                                     order_type=kite.ORDER_TYPE_MARKET,  tag="python_opening_{}".format(strikeSymbolCE)))
                key_name = "NFO:{}".format(strikeSymbolCE)
                last_traded_price = kite.ltp(key_name)
                python_orders = python_orders.append({'strikes':str(strikeSymbolCE), 'transaction_type':kite.TRANSACTION_TYPE_SELL, 'price':last_traded_price}, ignore_index = True)
                log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolCE, kite.TRANSACTION_TYPE_SELL, last_traded_price))

            # strikeTrades = len(zerodha_orders[zerodha_orders['tradingsymbol'] == strikeSymbolPE])
            strikeTrades = len(python_orders[python_orders['tradingsymbol'] == strikeSymbolPE])
            log.info("no of trades taken for symbol {} in order history is: {}".format(strikeSymbolPE, strikeTrades))
            if (strikeTrades%2) == 0:   # to check if there is 1 buy and 1 sell
                # python_orders.append(kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO, tradingsymbol=strikeSymbolPE, 
                #                                     transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=50, product=kite.PRODUCT_MIS, 
                #                                     order_type=kite.ORDER_TYPE_MARKET, tag="python_opening_{}".format(strikeSymbolPE)))
                key_name = "NFO:{}".format(strikeSymbolPE)
                last_traded_price = kite.ltp(key_name)
                python_orders = python_orders.append({'strikes':str(strikeSymbolPE), 'transaction_type':kite.TRANSACTION_TYPE_SELL, 'price':last_traded_price}, ignore_index = True)
                log.info("strike: {} | order_type: {} | price: {}".format(strikeSymbolPE, kite.TRANSACTION_TYPE_SELL, last_traded_price))
        else:
            time.sleep(5)
            zerodha_orders = pd.DataFrame(kite.orders())
            if (dt.datetime.now().minute%15 == 0) and (dt.datetime.now().second > 45):
                log.info("current nifty spot is: {}".format(nifty_curr_spot['last_price']))






# -*- coding: utf-8 -*-
import sys
import getopt
from market import Market, pyRofex
import time

try:
    ticker = sys.argv[1]
    login_data, args = getopt.getopt(sys.argv[2:], 'u:p:a:')
    user = login_data[0][1]
    password = login_data[1][1]
    if len(login_data) > 2:
        account = login_data[2][1]
    else:
        account = ""
except IndexError or getopt.GetoptError as e:
    print("""Error intentando leer el ticker y las credenciales de ingreso.
          Recuerde que el formato para llamar al script es:
          > challenge.py ticker -u USER -p PASSWORD -a ACCOUNT
          Si no ingresa el account, no podrá enviar órdenes al mercado""")
    print(e)
    sys.exit(2)

market = Market(user=user, password=password, account=account)

# %% Initialize market subscription
market.init_con()
tickers = ['DOOct20', 'DONov20']
market.subscription(tickers)
time.sleep(2)
# %% Envio orden al mercado
ticker = 'DOOct20'
try:
    last_md = market.ticker_last_price(ticker)
    last_bid = market.ticker_bid(ticker)

    if last_bid:
        market.send_order(ticker=ticker,
                          side=pyRofex.Side.BUY,
                          order_type=pyRofex.OrderType.LIMIT,
                          price=last_bid['price']-0.01,
                          size=1)
    else:
        market.send_order(ticker=ticker,
                          side=pyRofex.Side.BUY,
                          order_type=pyRofex.OrderType.LIMIT,
                          price=75.25,
                          size=1)


except Exception as e:
    print("Error ejecutando la estrategia")
    print(e)
    market.close_con()
    sys.exit(2)

#%% While para no cerrar el bot hasta que el usuario lo disponga.
# Para salir precionar ctrl + c
try:
    while True:
        pass
except KeyboardInterrupt:
    print("El usuario ha cerrado el programa")
    market.close_con()
    sys.exit(2)
except Exception as e:
    print("Ups, ocurrio el siguiente error, me cerraré luego de esto")
    print(e)
    sys.exit(2)

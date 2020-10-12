# -*- coding: utf-8 -*-
import pyRofex


class Market():
    def __init__(self, user, password, account=None, environment=pyRofex.Environment.REMARKET):
        self.environment = environment
        self.account = account
        self.is_initialized = False
        self.last_message = None  # last message received
        self.data = {}  # dict with all the market data
        self.open_orders = []
        self.available_instruments = set()
        self.orders = []

        try:
            pyRofex.initialize(user=user,
                               password=password,
                               account=account,
                               environment=environment)
            self.is_initialized = True
            self.available_instruments = self.get_instruments_list()
        except Exception as e:
            print("Error trying to initialize the connection")
            print(e)

    def market_data_handler(self, message):
        self.data[message['instrumentId']['symbol']].append({'timestamp': message['timestamp'],
                                                             'marketData': message['marketData']})
        self.last_message = message

    def order_report_handler(message):
        print("Market Data Message Received: {0}".format(message))

    def error_handler(self, message):
        print("Error Message Received: {0}".format(message))
        self.last_message = message

    def exception_handler(self, e):
        print("Exception Occurred: {0}".format(e.message))
        self.last_message = e

    def init_con(self):
        print("Iniciando sessión en "+self.environment.name)
        pyRofex.init_websocket_connection(market_data_handler=self.market_data_handler,
                                          error_handler=self.error_handler,
                                          exception_handler=self.exception_handler,
                                          order_report_handler=self.order_report_handler)
        if self.account:
            print("Subscribing to the account messages")
            pyRofex.order_report_subscription()
        else:
            print("Not logged in to the order report because there is no information about your account")

    def subscription(self, tickers, entries=None):
        if not self.is_initialized:
            raise ConnectionError("Operación no válida. Primero debe conectarse al mercado")

        if not entries:
            entries = [pyRofex.MarketDataEntry.BIDS,
                       pyRofex.MarketDataEntry.OFFERS,
                       pyRofex.MarketDataEntry.LAST]
        # create a list if the insput is just one ticker
        if isinstance(tickers, str):
            tickers = [tickers]
        for ticker in tickers:
            if ticker not in self.available_instruments:
                print(f"el instrumento {ticker} no se puede operar, revise la definición (incluído mayusculas y minusculas)")
            if ticker not in self.data.keys():
                # add the ticker to the data dictionary
                self.data[ticker] = []
        pyRofex.market_data_subscription(tickers=tickers,
                                         entries=entries)

    def get_instruments_list(self):
        if not self.is_initialized:
            raise ConnectionError("Operación no válida. Primero debe inicializar al mercado")
        response = pyRofex.get_all_instruments()
        instruments = set()
        if response['status'] != 'OK':
            raise "Response error when trying to ask for the list of instruments"
        else:
            for ticker in response['instruments']:
                instruments.add(ticker['instrumentId']['symbol'])
        return instruments

    def ticker_last_price(self, ticker):
        print(f"Consultando simbolo: {ticker}")
        if ticker in self.data.keys():
            last_price = self.data[ticker][-1]['marketData']['LA']
            print(f'Último precio operado para {ticker}: {last_price}')
        else:
            print('No estas suscripto a la este ticker')
            last_price = None
        return last_price

    def ticker_bid(self, ticker):
        print("Consultado BID")
        if ticker in self.data.keys():
            try:
                bid = self.data[ticker][-1]['marketData']['BI'][0]
                print(f'BID más alto para {ticker}: {bid}')
            except IndexError:
                bid = None
                print("No hay punta compradora")

        else:
            print('No estas suscripto a la este ticker')
            bid = None
        return bid

    def ticker_last_market_data(self, ticker):
        if ticker in self.data.keys():
            return self.data[ticker][-1]['marketData']
        else:
            print('No estas suscripto a la este ticker')
            return None

    def send_order(self, ticker, side, size, price=None, order_type=pyRofex.OrderType.LIMIT):
        """
        Enviar una orden al mercado

        Parameters
        ----------
        ticker : str
            Ticker del instrumento
        side : pyRofex.Side
            Lado (buy or sell)
        price : float
            Precio para emitir la orden, salvo que sea una orden market.
        size : int
            Tamaño de la orde .
        order_type : pyRofex.OrderType, optional
            Tipo de orden. The default is pyRofex.OrderType.LIMIT.

        Returns
        -------
        None.

        """

        print(f"Enviando una order al mercado para el instrumento {ticker}")
        if order_type == pyRofex.OrderType.MARKET:
            print(f"Side: {side.name}, Cant: {size}")
        else:
            if not price:
                raise ValueError("The price must be an input if the order type is not Market")
            price = round(price, 3)  # hago un round por si viene con muchos decimales, pq eso da error sino
            print(f"Side: {side.name}, Cant: {size}, Price: {price}")

        order = pyRofex.send_order(ticker=ticker,
                                   side=side,
                                   price=price,
                                   size=size,
                                   order_type=order_type)
        self.orders.append(order)

    def close_con(self):
        print("Cerrando sessión en "+self.environment.name)
        pyRofex.close_websocket_connection()
        self.is_initialized = False

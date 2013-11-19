# encoding=utf-8
import urllib2
import json
import logging
import threading
import datetime

USD_CNY_CURRENCY = None
CURRENCY_LAST_FETCH_DATE = None


def get_usd_cny_currency():
    CURRENCY_URL = "http://openexchangerates.org/api/latest.json?app_id=c6003cbd36254d80be3b41fb1a2012af"
    global USD_CNY_CURRENCY
    global CURRENCY_LAST_FETCH_DATE

    if USD_CNY_CURRENCY and CURRENCY_LAST_FETCH_DATE == datetime.date.today():
        return USD_CNY_CURRENCY
    else:
        fetcher = Fetcher('currency_fetcher')
        json_result = fetcher.get_request_result(CURRENCY_URL)
        result_dict = json.loads(json_result)
        try:
            USD_CNY_CURRENCY = result_dict['rates']['CNY']
            CURRENCY_LAST_FETCH_DATE = datetime.date.today()
            fetcher.logger.info("USD_CNY_CURRENCY: %s" % USD_CNY_CURRENCY)
            fetcher.logger.info("CURRENCY_LAST_FETCH_DATE: %s" % CURRENCY_LAST_FETCH_DATE)
            return USD_CNY_CURRENCY
        except KeyError, e:
            fetcher.logger.error("openexchangerates return unexpected data")
            return 0
        except Exception, e:
            fetcher.logger.error("Error: %s" % e)
            return 0


class FetcherThread(threading.Thread):
    """mutiple thread fetcher class"""
    def __init__(self, instance):
        super(FetcherThread, self).__init__(name=''.join(['thread_', instance.name]))
        self.instance = instance

    def run(self):
        self.instance.get_ticker()


class Fetcher(object):
    def __init__(self, name):
        self.name = name  # fetcher name
        self.fh, self.sh = self.logger_init()
        self.logger = logging.getLogger(name)
        self.logger.info(self.name + '__init__')

    def __del__(self):  # need more test
        self.logger.info(self.name + '__del__')
        self.fh.close()
        self.logger.removeHandler(self.fh)
        self.logger.removeHandler(self.sh)

    def logger_init(self):
        # filehandler logging
        fh = logging.FileHandler('logging.log')
        # console logging
        sh = logging.StreamHandler()

        # handler output formate
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        sh.setLevel(logging.DEBUG)

        # logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        # add handler to logger
        logger.addHandler(fh)
        logger.addHandler(sh)

        return [fh, sh]

    def get_request_result(self, url):
        # weixin waits 5s for each request
        TIMEOUT = 4
        try:
            result = urllib2.urlopen(url, timeout=TIMEOUT)
            if result.getcode() == 200:
                return result.read()
            else:
                return None
        except urllib2.HTTPError, e:
            self.logger.error("HTTPError: %d--%s" % (e.code, e.reason))
            return None
        except urllib2.URLError, e:
            self.logger.error("URLError: %s" % e.reason)
            return None
        except Exception as e:
            self.logger.error("Error: %s" % e)
            return None

    def get_ticker(self, ticker_url):
        ticker_json = self.get_request_result(ticker_url)
        if ticker_json:  # ticker_json is *not* None or empty string
            return json.loads(ticker_json)
        else:
            return None

    #@property
    #def nonce(self):
        #if self.error:
            #return self.error
        #return str(int(time.time() * 1e6))


class Mtgox(Fetcher):
    TICKER_URL_USD = 'https://data.mtgox.com/api/2/BTCUSD/money/ticker'
    TICKER_URL_CNY = 'https://data.mtgox.com/api/2/BTCCNY/money/ticker'

    def __init__(self, name='mtgox', currency='USD'):
        self.error = None
        self.ticker = None
        if currency == 'USD':
            self.ticker_url = self.TICKER_URL_USD
        elif currency == 'CNY':
            self.ticker_url = self.TICKER_URL_CNY
        super(Mtgox, self).__init__(name)

    def get_ticker(self):
        """must been called before following properties"""
        self.ticker = super(Mtgox, self).get_ticker(self.ticker_url)
        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % self.name
        elif self.ticker['result'] != 'success':
            self.error = u'%s已返回数据，但内容错误' % self.name

    @property
    def last_all(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['data']['last_all']['value'])
        except Exception:
            return 0

    @property
    def high(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['data']['high']['value'])
        except Exception:
            return 0

    @property
    def low(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['data']['low']['value'])
        except Exception:
            return 0

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return 0
        try:
            return self.ticker['data']['vol']['display_short']
        except Exception:
            return 0

    @property
    def vwap(self):
        """the volume-weighted average price"""
        if self.error:
            return 0
        try:
            return float(self.ticker['data']['vwap']['value'])
        except Exception:
            return 0

    @property
    def last_buy(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['data']['buy']['value'])
        except Exception:
            return 0

    @property
    def last_sell(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['data']['sell']['value'])
        except Exception:
            return 0


class BTCE(Fetcher):
    TICKER_URL = 'https://btc-e.com/api/2/%s/ticker'

    def __init__(self, name='btc-e', coin='btc_usd'):
        self.error = None
        self.ticker = None
        self.coin = coin
        super(BTCE, self).__init__(name)

    def get_ticker(self):
        self.ticker = super(BTCE, self).get_ticker(self.TICKER_URL % self.coin)

        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % self.name
        elif 'ticker' not in self.ticker:
            self.error = u'%s已返回数据，但内容错误' % self.name

    @property
    def last_all(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['last'])
        except Exception:
            return 0

    @property
    def high(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['high'])
        except Exception:
            return 0

    @property
    def low(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['low'])
        except Exception:
            return 0

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['vol_cur'])
        except Exception:
            return 0

    @property
    def last_buy(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['buy'])
        except Exception:
            return 0

    @property
    def last_sell(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['sell'])
        except Exception:
            return 0


class BTCChina(Fetcher):
    TICKER_URL = 'https://data.btcchina.com/data/ticker'

    def __init__(self, name='btcchina'):
        self.error = None
        self.ticker = None
        super(BTCChina, self).__init__(name)

    def get_ticker(self):
        self.ticker = super(BTCChina, self).get_ticker(self.TICKER_URL)

        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % self.name
        elif 'ticker' not in self.ticker:
            self.error = u'%s已返回数据，但内容错误' % self.name

    @property
    def last_all(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['last'])
        except Exception:
            return 0

    @property
    def high(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['high'])
        except Exception:
            return 0

    @property
    def low(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['low'])
        except Exception:
            return 0

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['vol'])
        except Exception:
            return 0

    @property
    def last_buy(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['buy'])
        except Exception:
            return 0

    @property
    def last_sell(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['sell'])
        except Exception:
            return 0


class Fxbtc(Fetcher):
    TICKER_URL = 'https://www.fxbtc.com/jport?op=query&type=ticker&symbol=%s'

    def __init__(self, name='fxbtc', coin='btc_cny'):
        self.error = None
        self.ticker = None
        self.coin = coin
        super(Fxbtc, self).__init__(name)

    def get_ticker(self):
        self.ticker = super(Fxbtc, self).get_ticker(self.TICKER_URL % self.coin)

        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % self.name
        elif 'ticker' not in self.ticker:
            self.error = u'%s已返回数据，但内容错误' % self.name

    @property
    def last_all(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['last_rate'])
        except Exception:
            return 0

    @property
    def high(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['high'])
        except Exception:
            return 0

    @property
    def low(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['low'])
        except Exception:
            return 0

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['vol'])
        except Exception:
            return 0

    @property
    def last_buy(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['bid'])
        except Exception:
            return 0

    @property
    def last_sell(self):
        if self.error:
            return 0
        try:
            return float(self.ticker['ticker']['ask'])
        except Exception:
            return 0


class CN42BTC(Fetcher):
    TICKER_URL = 'http://42btc.sinaapp.com/api/trend/ticker/0/1'

    def __init__(self, name='42btc'):
        self.error = None
        self.ticker = None
        super(CN42BTC, self).__init__(name)

    def get_ticker(self):
        self.ticker = super(CN42BTC, self).get_ticker(self.TICKER_URL)

        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % self.name
        elif not isinstance(self.ticker, list):
            self.error = u'%s已返回数据，但内容错误' % self.name

    @property
    def last_all(self):
        if self.error:
            return 0
        try:
            return float(self.ticker[0])
        except Exception:
            return 0

    @property
    def high(self):
        if self.error:
            return 0
        try:
            return float(self.ticker[1])
        except Exception:
            return 0

    @property
    def low(self):
        if self.error:
            return 0
        try:
            return float(self.ticker[2])
        except Exception:
            return 0

    @property
    def average(self):
        if self.error:
            return 0
        try:
            return float(self.ticker[3])
        except Exception:
            return 0

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return 0
        try:
            return float(self.ticker[4])
        except Exception:
            return 0

    @property
    def last_buy(self):
        if self.error:
            return 0
        try:
            return float(self.ticker[5])
        except Exception:
            return 0

    @property
    def last_sell(self):
        if self.error:
            return 0
        try:
            return float(self.ticker[6])
        except Exception:
            return 0

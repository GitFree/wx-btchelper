# encoding=utf-8
import urllib2
import urllib
import json
import time
import logging


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
        try:
            result = urllib2.urlopen(url)
            if result.getcode() == 200:
                return result.read()
            else:
                return None
        except urllib2.HTTPError, e:
            self.logger.error("HTTPError: %d--%s" % (e.code, e.reason))
            return None
        except urllib2.URLError, e:
            self.logger.error("URLError: %s" + e.reason)
            return None

    def get_ticker(self, ticker_url):
        ticker_json = self.get_request_result(ticker_url)
        if ticker_json:  # ticker_json is *not* (None or empty string)
            return json.loads(ticker_json)
        else:
            return None

    @property
    def nonce(self):
        if self.error:
            return self.error
        return str(int(time.time() * 1e6))


class Mtgox(Fetcher):
    TICKER_URL = 'https://data.mtgox.com/api/2/BTCUSD/money/ticker'

    def __init__(self, name='mtgox'):
        self.error = None
        super(Mtgox, self).__init__(name)
        self.ticker = super(Mtgox, self).get_ticker(self.TICKER_URL)
        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % name
            # raise a web or website error exception
        elif self.ticker['result'] != 'success':
            self.error = u'%s返回了错误的响应' % name
            # raise a wrong response content exception

    def get_ticker_with_auth(self):
        param = {'nonce': super.nonce}
        post_data = urllib.urlencode(param)
        request = self.get_request('/BTCUSD/money/ticker', post_data)
        ticker_file = urllib2.urlopen(request, post_data)
        self.ticker = json.loads(ticker_file.read())
        if self.ticker['result'] != 'success':
            pass  # raise a customer exception

    @property
    def last_all(self):
        if self.error:
            return self.error
        return self.ticker['data']['last_all']['display_short']

    @property
    def high(self):
        if self.error:
            return self.error
        return self.ticker['data']['high']['display_short']

    @property
    def low(self):
        if self.error:
            return self.error
        return self.ticker['data']['low']['display_short']

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return self.error
        return self.ticker['data']['vol']['display_short']

    @property
    def vwap(self):
        """the volume-weighted average price"""
        if self.error:
            return self.error
        return self.ticker['data']['vwap']['display_short']

    @property
    def last_buy(self):
        if self.error:
            return self.error
        return self.ticker['data']['buy']['display_short']

    @property
    def last_sell(self):
        if self.error:
            return self.error
        return self.ticker['data']['sell']['display_short']


class BTCE(Fetcher):
    TICKER_URL = 'https://btc-e.com/api/2/%s/ticker'

    def __init__(self, name='btc-e', coin='btc_usd'):
        self.error = None
        super(BTCE, self).__init__(name)
        self.ticker = super(BTCE, self).get_ticker(self.TICKER_URL % coin)

        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % name
            # raise a web or website error exception
        elif 'ticker' not in self.ticker:
            self.error = u'%s返回非预期的响应' % name
            # raise a wrong response content exception

    @property
    def last_all(self):
        if self.error:
            return self.error
        return self.ticker['ticker']['last']

    @property
    def high(self):
        if self.error:
            return self.error
        return self.ticker['ticker']['high']

    @property
    def low(self):
        if self.error:
            return self.error
        return self.ticker['ticker']['low']

    @property
    def volume(self):
        """the volume traded today"""
        if self.error:
            return self.error
        return self.ticker['ticker']['vol_cur']

    @property
    def last_buy(self):
        if self.error:
            return self.error
        return self.ticker['ticker']['buy']

    @property
    def last_sell(self):
        if self.error:
            return self.error
        return self.ticker['ticker']['sell']

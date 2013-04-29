# encoding=utf-8
import urllib2
import urllib
import json
import hmac
import base64
import hashlib
import time
import logging


class Fetcher(object):
    name = ''  # fetcher name

    def __init__(self, name):
        self.name = name
        self.logger_init()
        self.logger = logging.getLogger(self.name)
        self.logger.info(self.name + '__init__')

    def logger_init(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # filehandler logging
        flog = logging.FileHandler('logging.log')
        flog.setLevel(logging.DEBUG)

        # console logging
        clog = logging.StreamHandler()
        clog.setLevel(logging.DEBUG)

        # handler output formate
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        flog.setFormatter(formatter)
        clog.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(flog)
        logger.addHandler(clog)

    def get_request_result(self, url):
        try:
            result = urllib2.urlopen(url)
            if result.getcode() == 200:
                return result.read()
            else:
                return None
        except urllib2.HTTPError, e:
            self.logger.error(e.code)
            return None
        except urllib2.URLError, e:
            self.logger.error(e.reason)
            return None


class Mtgox(Fetcher):
    base_url = 'https://data.mtgox.com/api/2'
    key = '1a5f964c-b849-4db3-b80b-82010aa1c625'  # keyname:btchelper_no_permission
    secret = 'nAzhkooonbct/epAwJEZZGZ0IqvvKFxErdVJY6/rdVEbcPoeh/IX+6tpiNzmqSAQ2niMKn7kDjxhA3FTWs+VoA=='
    ticker = None
    error = ''

    def __init__(self, name='mtgox'):
        super(Mtgox, self).__init__(name)
        self.ticker = self.get_ticker()
        if self.ticker is None:
            self.error = u'访问%s时发生网络故障' % name
            # raise a web or website error exception
        elif self.ticker['result'] != 'success':
            self.error = u'%s返回了错误的响应' % name
            # raise a wrong response content exception

    def get_ticker(self):
        ticker_url = '/BTCUSD/money/ticker'
        ticker_json = super(Mtgox, self).get_request_result(self.base_url + ticker_url)
        if ticker_json:
            return json.loads(ticker_json)
        else:
            return None

    def get_request_with_auth(self, path, post_data=None):
        hash_data = path + chr(0) + post_data
        secret = base64.b64decode(self.secret)
        sha512 = hashlib.sha512
        hmac_str = hmac.new(secret, hash_data, sha512).digest()
        header = {
            'User-Agent': 'BTCHelper',
            'Rest-Key': self.key,
            'Rest-Sign': base64.b64encode(hmac_str),
        }
        return urllib2.Request(self.base_url + path, post_data, header)

    def get_ticker_with_auth(self):
        param = {'nonce': self.nonce}
        post_data = urllib.urlencode(param)
        request = self.get_request('/BTCUSD/money/ticker', post_data)
        ticker_file = urllib2.urlopen(request, post_data)
        self.ticker = json.loads(ticker_file.read())
        print '**********************'
        print self.ticker
        print '**********************'
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
        """the volume-weighted average price"""
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

    @property
    def nonce(self):
        if self.error:
            return self.error
        return str(int(time.time() * 1e6))

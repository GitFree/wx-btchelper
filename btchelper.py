#encoding=utf-8
from bottle import request, get, post, debug, run, default_app
import hashlib
import time
import xml.etree.ElementTree as ET
import settings
from fetcher import Mtgox, BTCE, BTCChina, Fxbtc, CN42BTC
from fetcher import FetcherThread, get_usd_cny_currency


WEIXIN_TOKEN = '55ac87b3ffb018bd583248873385f775'


class ResponsePost():
    def __init__(self, msg_dic):
        self.msg_dic = msg_dic

    def nonce():
        return str(int(time.time() * 1e6))

    def response_txt(self, content, flag=0):
        """response a text message

        flag  0--DONT star this message
              1--star this message
        """
        return settings.RESPONSE_TXT % (
            self.msg_dic['FromUserName'],
            self.msg_dic['ToUserName'],
            int(time.time()),
            'text',
            content,
            flag)

    def help_info(self):
        """帮助信息
        """
        return self.response_txt(settings.RESPONSE_HELP)

    def btc(self):
        mt_usd = Mtgox(currency='USD')
        #mt_cny = Mtgox(currency='CNY')
        btce = BTCE()
        btcc = BTCChina()
        fxbtc = Fxbtc()
        cn42btc = CN42BTC()
        list_instance = [mt_usd, btce, btcc, fxbtc, cn42btc]

        list_thread = []
        for instance in list_instance:
            t = FetcherThread(instance)
            list_thread.append(t)
            t.daemon = True
            t.start()

        # wait for all thread finish
        for t in list_thread:
            t.join()

        for instance in list_instance:
            if instance.error:
                instance = None

        usd_cny_currency = get_usd_cny_currency()

        content = u"""比特币实时行情汇总
----------------
Mtgox价格：$%.2f，合￥%.2f
MtGox日交量：%s

BTC-E价格：$%.2f，合￥%.2f
BTC-E日交量：%.4f BTC

BTCChina价格：￥%.2f
BTCChina日交量：%.4f BTC

FXBTC价格：￥%.2f
FXBTC日交量：%.4f BTC

42BTC价格：￥%.2f
42BTC日交量：%.4f BTC
""" %\
            (0 if mt_usd is None else mt_usd.last_all,
             mt_usd.last_all * usd_cny_currency,
             0 if mt_usd is None else mt_usd.volume,
             0 if btce is None else btce.last_all,
             btce.last_all * usd_cny_currency,
             0 if btce is None else btce.volume,
             0 if btcc is None else btcc.last_all,
             0 if btcc is None else btcc.volume,
             0 if fxbtc is None else fxbtc.last_all,
             0 if fxbtc is None else fxbtc.volume,
             0 if fxbtc is None else cn42btc.last_all,
             0 if fxbtc is None else cn42btc.volume)

        return self.response_txt(content)

    def ltc(self):
        btce_ltcusd = BTCE(coin='ltc_usd')
        btce_ltcbtc = BTCE(coin='ltc_btc')
        fx_ltccny = Fxbtc(coin='ltc_cny')
        fx_ltcbtc = Fxbtc(coin='ltc_btc')
        list_instance = [btce_ltcusd, btce_ltcbtc, fx_ltccny, fx_ltcbtc]

        list_thread = []
        for instance in list_instance:
            t = FetcherThread(instance)
            list_thread.append(t)
            t.daemon = True
            t.start()

        # wait for all thread finish
        for t in list_thread:
            t.join()

        for instance in list_instance:
            if instance.error:
                instance = None

        usd_cny_currency = get_usd_cny_currency()

        content = u"""利特币实时行情汇总
-----------------
BTC-E价格1：$%.2f，合￥%.2f
BTC-E价格2：%.4f BTC
BTC-E日交量：%.2f LTC

FXBTC价格1：￥%.2f
FXBTC价格2：%.4f BTC
FXBTC日交量：%.2f LTC""" %\
            (0 if btce_ltcusd is None else btce_ltcusd.last_all,
             btce_ltcusd.last_all * usd_cny_currency,
             0 if btce_ltcbtc is None else btce_ltcbtc.last_all,
             0 if (btce_ltcusd and btce_ltcbtc) is None else btce_ltcusd.volume + btce_ltcbtc.volume,
             0 if fx_ltccny is None else fx_ltccny.last_all,
             0 if fx_ltcbtc is None else btce_ltcbtc.last_all,
             0 if (fx_ltccny and fx_ltcbtc) is None else fx_ltccny.volume + fx_ltcbtc.volume)
        return self.response_txt(content)

    def mtgox(self):
        mt_usd = Mtgox(currency='USD')
        mt_usd.get_ticker()

        if mt_usd.error:
            return self.response_txt(mt_usd.error)

        usd_cny_currency = get_usd_cny_currency()

        content = u"""MtGox比特币实时行情
---------------
最新成交价：$%.2f，合￥%.2f
日交量：%s
最高成交价：$%.2f，合￥%.2f
最低成交价：$%.2f，合￥%.2f
最新买入价：$%.2f，合￥%.2f
最新卖出价：$%.2f，合￥%.2f
加权平均价：$%.2f，合￥%.2f""" %\
            (mt_usd.last_all,
             mt_usd.last_all * usd_cny_currency,
             mt_usd.volume,
             mt_usd.high,
             mt_usd.high * usd_cny_currency,
             mt_usd.low,
             mt_usd.low * usd_cny_currency,
             mt_usd.last_buy,
             mt_usd.last_buy * usd_cny_currency,
             mt_usd.last_sell,
             mt_usd.last_sell * usd_cny_currency,
             mt_usd.vwap,
             mt_usd.vwap * usd_cny_currency)
        return self.response_txt(content)

    def btce(self):
        btce = BTCE()
        btce.get_ticker()
        if btce.error:
            return self.response_txt(btce.error)

        usd_cny_currency = get_usd_cny_currency()

        content = u"""BTC-E比特币实时行情
---------------
最新成交价：$%.2f，合￥%.2f
日交量：%.4f BTC
最高成交价：$%.2f，合￥%.2f
最低成交价：$%.2f，合￥%.2f
最新买入价：$%.2f，合￥%.2f
最新卖出价：$%.2f，合￥%.2f""" %\
            (btce.last_all,
             btce.last_all * usd_cny_currency,
             btce.volume,
             btce.high,
             btce.high * usd_cny_currency,
             btce.low,
             btce.low * usd_cny_currency,
             btce.last_buy,
             btce.last_buy * usd_cny_currency,
             btce.last_sell,
             btce.last_sell * usd_cny_currency)
        return self.response_txt(content)

    def btcchina(self):
        btcc = BTCChina()
        btcc.get_ticker()
        if btcc.error:
            return self.response_txt(btcc.error)

        content = u"""BTCChina比特币实时行情
---------------
最新成交价：￥%.2f
日交量：%.4f BTC
最高成交价：￥%.2f
最低成交价：￥%.2f
最新买入价：￥%.2f
最新卖出价：￥%.2f""" %\
            (btcc.last_all, btcc.volume, btcc.high,
                btcc.low, btcc.last_buy, btcc.last_sell)
        return self.response_txt(content)

    def fxbtc(self):
        fxbtc = Fxbtc()
        fxbtc.get_ticker()
        if fxbtc.error:
            return self.response_txt(fxbtc.error)

        content = u"""FXBTC比特币实时行情
---------------
最新成交价：￥%.2f
日交量：%.4f BTC
最高成交价：￥%.2f
最低成交价：￥%.2f
最新买入价：￥%.2f
最新卖出价：￥%.2f""" %\
            (fxbtc.last_all, fxbtc.volume, fxbtc.high,
                fxbtc.low, fxbtc.last_buy, fxbtc.last_sell)
        return self.response_txt(content)

    def cn42btc(self):
        cn42btc = CN42BTC()
        cn42btc.get_ticker()
        if cn42btc.error:
            return self.response_txt(cn42btc.error)

        content = u"""42BTC比特币实时行情
---------------
最新成交价：￥%.2f
日交量：%.4f BTC
最高成交价：￥%.2f
最低成交价：￥%.2f
平均成交价：￥%.2f
最新买入价：￥%.2f
最新卖出价：￥%.2f""" %\
            (cn42btc.last_all, cn42btc.volume, cn42btc.high,
             cn42btc.low, cn42btc.average, cn42btc.last_buy, cn42btc.last_sell)
        return self.response_txt(content)

    def todo(self):
        """TODO list"""
        return self.response_txt(settings.RESPONSE_TODO)

    def others(self):
        return self.response_txt(u'不支持的命令，输入 h 或 help 查看帮助。', 1)


def recvmsg2dic():
    """parse received message to dictionary
    """
    recvmsg = request.body.read()
    root = ET.fromstring(recvmsg)
    msg_dic = {}
    for child in root:
        msg_dic[child.tag] = child.text
    return msg_dic


def handle_post(msg_dic):
    resp = ResponsePost(msg_dic)
    if msg_dic['MsgType'] == 'event':
        if msg_dic['Event'] == 'subscribe':  # new user subscribe
            return resp.response_txt(settings.RESPONSE_SUBSCRIBE)
    elif msg_dic['MsgType'] != 'text':  # only text post supported
        return resp.response_txt(settings.RESPONSE_UNSUPPORTED_TYPE, 1)
    else:  # text type post received
        content = msg_dic['Content'].lower().strip()
        if content in settings.KEYWORDS_DIC['help']:
            return resp.help_info()
        if content in settings.KEYWORDS_DIC['btc']:
            return resp.btc()
        if content in settings.KEYWORDS_DIC['ltc']:
            return resp.ltc()
        if content in settings.KEYWORDS_DIC['mtgox']:
            return resp.mtgox()
        if content in settings.KEYWORDS_DIC['btce']:
            return resp.btce()
        if content in settings.KEYWORDS_DIC['btcchina']:
            return resp.btcchina()
        if content in settings.KEYWORDS_DIC['fxbtc']:
            return resp.fxbtc()
        if content in settings.KEYWORDS_DIC['42btc']:
            return resp.cn42btc()
        if content in settings.KEYWORDS_DIC['todo']:
            return resp.todo()

        return resp.others()


@get('/btchelper')
def check_signature():
    """check if the get request was from winxin.

        1.sorting signature,timestamp,nonce
        2.sha1 the three args
        3.return echoStr to winxin
    """
    global WEIXIN_TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echoStr = request.GET.get("echostr", None)

    token = WEIXIN_TOKEN
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    print tmpstr
    if tmpstr == signature:
        return echoStr
    else:
        return 'signature wrong!!'


@post('/btchelper')
def response_post():
    msg_dic = recvmsg2dic()
    return handle_post(msg_dic)


if __name__ == "__main__":
    # bottle run mode
    debug(True)
    run(host='0.0.0.0', port=5050, reloader=True)
else:
    import os
    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))

    # Do NOT use bottle.run() with mod_wsgi
    application = default_app()

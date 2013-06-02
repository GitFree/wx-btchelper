#encoding=utf-8
from bottle import request, get, post, debug, run, default_app
import hashlib
import time
import xml.etree.ElementTree as ET
import settings
from fetcher import Mtgox, BTCE, BTCChina, Fxbtc, FetcherThread


TOKEN = '55ac87b3ffb018bd583248873385f775'


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
        mt = Mtgox()
        btce = BTCE()
        btcc = BTCChina()
        fxbtc = Fxbtc()
        list_instance = [mt, btce, btcc, fxbtc]

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
                return self.response_txt(instance.error)

        content = u"""比特币实时行情汇总
----------------
MtGox价格：%s
MtGox日交量：%s

BTC-E价格：$%.2f
BTC-E日交量：%.4f BTC

BTCChina价格：￥%s
BTCChina日交量：%.4f BTC

FXBTC价格：￥%.2f
FXBTC日交量：%.4f BTC""" %\
            (mt.last_all, mt.volume,
             btce.last_all, btce.volume,
             btcc.last_all, btcc.volume,
             fxbtc.last_all, fxbtc.volume)

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
                return self.response_txt(instance.error)

        content = u"""利特币实时行情汇总
-----------------
BTC-E价格1：$%.2f
BTC-E价格2：%.4f BTC
BTC-E日交量：%.2f LTC

FXBTC价格1：￥%.2f
FXBTC价格2：%.4f BTC
FXBTC日交量：%.2f LTC""" %\
            (btce_ltcusd.last_all,
             btce_ltcbtc.last_all,
             btce_ltcbtc.volume + btce_ltcbtc.volume,
             fx_ltccny.last_all,
             fx_ltcbtc.last_all,
             fx_ltccny.volume + fx_ltcbtc.volume)
        return self.response_txt(content)

    def mtgox(self):
        mt = Mtgox()
        mt.get_ticker()
        if mt.error:
            return self.response_txt(mt.error)

        content = u"""MtGox比特币实时行情
---------------
最新成交价：%s
日交量：%s
最高成交价：%s
最低成交价：%s
最新买入价：%s
最新卖出价：%s
加权平均价：%s""" %\
            (mt.last_all, mt.volume, mt.high, mt.low,
             mt.last_buy, mt.last_sell, mt.vwap)
        return self.response_txt(content)

    def btce(self):
        btce = BTCE()
        btce.get_ticker()
        if btce.error:
            return self.response_txt(btce.error)

        print "***btce****"
        print btce.error
        print "***btce***"
        content = u"""BTC-E比特币实时行情
---------------
最新成交价：$%.2f
日交量：%.4f BTC
最高成交价：$%.2f
最低成交价：$%.2f
最新买入价：$%.2f
最新卖出价：$%.2f""" %\
            (btce.last_all, btce.volume, btce.high,
                btce.low, btce.last_buy, btce.last_sell)
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
        return self.response_txt(u'暂不不支持的命令，输入 h 或 help 查看帮助。', 1)

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
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echoStr = request.GET.get("echostr", None)

    token = TOKEN
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
    run(host='0.0.0.0', port=8002, reloader=True)
else:
    import os
    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))

    # Do NOT use bottle.run() with mod_wsgi
    application = default_app()

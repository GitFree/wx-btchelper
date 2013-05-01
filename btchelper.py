#encoding=utf-8
from bottle import request, get, post, debug, run, default_app
import hashlib
import time
import xml.etree.ElementTree as ET
import settings
from fetcher import Mtgox, BTCE


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
        content = u"比特币实时价格汇总\
       \r\n--------------------\
       \r\nMtGox实时价格：%s\
       \r\nMtGox日交量：%s\
       \r\n\
       \r\nBTC-E实时价格：$%s\
       \r\nBTC-E日成交量：%s BTC" %\
            (mt.last_all, mt.volume, btce.last_all, btce.volume)
        return self.response_txt(content)

    def ltc(self):
        pass

    def mtgox(self):
        mt = Mtgox()
        content = u"MtGox实时信息\
        \r\n---------------\
        \r\n最新成交价：%s\
        \r\n日交量：%s\
        \r\n最高成交价：%s\
        \r\n最低成交价：%s\
        \r\n最新买入价：%s\
        \r\n最新卖出价：%s\
        \r\n加权平均价：%s" %\
            (mt.last_all, mt.volume, mt.high, mt.low,
             mt.last_buy, mt.last_sell, mt.vwap)
        return self.response_txt(content)

    def btce(self):
        btce = BTCE()
        content = u"BTC-E实时信息\
        \r\n---------------\
        \r\n最新成交价：$%s\
        \r\n日交量：%s BTC\
        \r\n最高成交价：$%s\
        \r\n最低成交价：$%s\
        \r\n最新买入价：$%s\
        \r\n最新卖出价：$%s" %\
            (btce.last_all, btce.volume, btce.high,
                btce.low, btce.last_buy, btce.last_sell)
        return self.response_txt(content)

    def btcchina(self):
        pass

    def cn42btc(self):
        pass

    def others(self):
        return self.response_txt(u'不支持的命令，输入 h 或 help 查看帮助', 1)


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
        return resp.response_txt(settings.RESPONSE_SUBSCRIBE, 1)
    else:  # text type post received
        content = msg_dic['Content'].lower()
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
        if content in settings.KEYWORDS_DIC['42btc']:
            return resp.cn42btc()

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

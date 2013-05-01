#encoding=utf-8


POST_TXT = """
            <xml>
                <ToUserName><![CDATA[toUser]]></ToUserName>
                <FromUserName><![CDATA[fromUser]]></FromUserName>
                <CreateTime>1348831860</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[this is a test]]></Content>
                <MsgId>1234567890123456</MsgId>
            </xml>
            """

RESPONSE_TXT = '''
            <xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>%d</FuncFlag>
            </xml>
            '''

#need to init
RESPONSE_TXT_PIC = """
            <xml>
                <ToUserName><![CDATA[toUser]]></ToUserName>
                <FromUserName><![CDATA[fromUser]]></FromUserName>
                <CreateTime>12345678</CreateTime>
                <MsgType><![CDATA[news]]></MsgType>
                <ArticleCount>2</ArticleCount>
                <Articles>
                <item>
                <Title><![CDATA[title1]]></Title>
                <Description><![CDATA[description1]]></Description>
                <PicUrl><![CDATA[picurl]]></PicUrl>
                <Url><![CDATA[url]]></Url>
                </item>
                <item>
                <Title><![CDATA[title]]></Title>
                <Description><![CDATA[description]]></Description>
                <PicUrl><![CDATA[picurl]]></PicUrl>
                <Url><![CDATA[url]]></Url>
                </item>
                </Articles>
                <FuncFlag>0</FuncFlag>
            </xml>
            """

KEYWORDS_DIC = {
    'help': ('help', 'h', '?', '？', u'帮助',),
    'btc': ('btc', u'比特币', u'汇率', u'价格',),
    'ltc': ('ltc', u'利特币',),
    'mtgox': ('mtgox', 'mt', 'gox'),
    'btce': ('btce', 'btc-e',),
    'btcchina': ('btcc', 'btcchina',),
    '42btc': ('42btc',),
}

RESPONSE_SUBSCRIBE = u"欢迎关注比特币助手，比特币助手可以随时随地查询比特币、利特币实时价格，\
                        不定期推送比特币、利特币最新资讯。\
                        \r\n输入h或help查看帮助。"

RESPONSE_HELP = u"目前支持的命令：\
            \r\n比特币实时价格汇总 -- btc 或 比特币\
            \r\nMtGox实时交易信息  -- mtgox 或 mt 或 gox\
            \r\nBTC-E实时交易信息  -- btce 或 btc-e\
            \r\n\
            正在开发中的命令：\
            \r\n利特币实时价格汇总 -- ltc 或 利特币\
            \r\nBTCChina实时交易信息 -- btcc 或 btcchina\
            \r\n42BTC实时交易信息  -- 42btc"

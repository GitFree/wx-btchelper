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
                <FuncFlag>%s</FuncFlag>
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

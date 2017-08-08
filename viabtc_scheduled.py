# -*- coding: UTF-8 -*- 
import sys, os, hashlib
import urllib2
import const
import json
import time  
import sched
import logging  
import logging.handlers  

const.LOG_FILE = "viabtc_scheduled.txt"

#定投类型常量定义
const.BTCCNY = "BTCCNY"
const.BCCCNY = "BCCCNY"
const.BCCBTC = "BCCBTC"

const.ORDER_TYPE_SELL = 'sell'
const.ORDER_TYPE_BUY = 'buy'
#===========================================================
#config start
#viabtc api
const.ACCESS_ID = "YOUR_ACCESS_ID"
const.SECRET_KEY = "YOUR_SECRET_KEY"
#定投金额
# BTCCNY和BCCCNY 单位 CNY
# BCCBTC        单位 BTC
# 
const.ORDER_AMOUNT = 30
#定投类型
const.ORDER_MARKET = const.BCCCNY
#账户限额,保留一部分钱，账户达到最低限额就停止定投
# BTCCNY和BCCCNY  CNY账户
# BCCBTC          BTC账户
const.ACCOUNT_LIMIT = 1500
#定投间隔,单位秒, 
# 每分钟=60 每小时= 60*60  每天=24*60*60 每周=7*24*60*60 
const.ORDER_TIME_INTERVAL = 30

#config end
#==============================================================


BASE_URL = 'https://www.viabtc.com/api/v1'

Account = {'CNY':0,'BTC':0,'BCC':0}

try:
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
except ImportError:
    # Adaptions for Python 2 compatibility.
    import urllib2
    from urllib import urlencode
    from urllib2 import urlopen
    class Request(urllib2.Request):
        def __init__(self, *args, **kwargs):
            self._method = kwargs.pop('method', None)
            urllib2.Request.__init__(self, *args, **kwargs)

        def get_method(self):
            return self._method if self._method else urllib2.Request.get_method(self)

def _filter_urlencode(items):
    return urlencode({k: v for k, v in items if v is not None})

def _request(endpoint, **kwargs):
    if kwargs:
        endpoint = '%s?' % endpoint
        params = _filter_urlencode(kwargs.items())
    else:
        params = ''
    
    url = '%s/%s%s' % (BASE_URL, endpoint, params)
    request = Request(url)
    request.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1")
    try:
        response = urlopen(request)
    except urllib2.URLError, e:
        print e
        
        return None
    content = response.read()
    return json.loads(content)


def _signed_request(endpoint, method='POST', **kwargs):
    kwargs['access_id'] = const.ACCESS_ID
    signature = _sign_params(kwargs)
    params = _filter_urlencode(kwargs.items())
 
    if method == 'GET':
        requrl = '%s%s?%s' % (BASE_URL, endpoint, params)
        data = None
    else:
        requrl = '%s%s' % (BASE_URL, endpoint)
        data = json.dumps(kwargs).encode('utf8')

    request = Request(requrl, data=data, method=method)
    request.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1")
    request.add_header('content-type', 'application/json')
    request.add_header('authorization',signature)

    try :
        response = urlopen(request)
    except urllib2.URLError, e:
        print e
        return None
    content = response.read().decode('utf8')

    result = json.loads(content)

    return result
def _sign_params(params):
    params['access_id'] = const.ACCESS_ID
    sorted_params = sorted(params.items())
    ordered_params = '&'.join('%s=%s' % (k, v) for k, v in sorted_params
            if v is not None)
    ordered_params = '%s&secret_key=%s' % (ordered_params, const.SECRET_KEY)

    sig = hashlib.md5(ordered_params.encode('utf8')).hexdigest().upper()
    return sig


def market_ticker(market):
    return _request('/market/ticker', market=market)

def market_depth(market, merge=0, limit=None):
    return _request('/market/depth', market=market, merge=merge, limit=limit)

def market_deals(market, last_id=None):
    return _request('/market/deals', market=market, last_id=last_id)

def market_kline(market, period):
    return _request('/market/kline', market=market, type=period)


def account_balance():
    return _signed_request('/balance/', 'GET')

def trade_limit_order(market, order_type, amount, price, source_id=None):
    return _signed_request('/order/limit',
            market=market, type=order_type, amount=amount, price=price,
            source_id=source_id)

def trade_market_order(market, order_type, amount):
    
    return _signed_request('/order/market',
            market=market, type=order_type, amount=amount)

def trade_cancel(market, order_id):
    return _signed_request('/order/pending', 'DELETE',
            market=market, order_id=order_id)

def trade_pending(market, page=1, limit=100):
    return _signed_request('/order/pending', 'GET',
            market=market, page=page, limit=limit)

def trade_finished(market, page=1, limit=100):
    return _signed_request('/order/finished', 'GET',
            market=market, page=page, limit=limit)

def float_decimal(val,decimal):
    format = '%.'+str(decimal)+'f'
    return float(format % float(val))

def check_balance():
    data = account_balance()
    if data and data['code'] ==0 :
        Account['CNY'] = float_decimal(data['data']['CNY']['available'],2)
        Account['BTC'] = float_decimal(data['data']['BTC']['available'],2)
        Account['BCC'] = float_decimal(data['data']['BCC']['available'],2)
    else:
        print data['message']
        return False
    if const.ORDER_MARKET == const.BTCCNY or const.ORDER_MARKET == const.BCCCNY :
        if Account['CNY'] <= const.ACCOUNT_LIMIT :
            return False
        else:
            return True
    else:
        if Account['BTC'] <= const.ACCOUNT_LIMIT:
            return False
        else:
            return True


handler = logging.handlers.RotatingFileHandler(const.LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler   
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  
  
formatter = logging.Formatter(fmt)   # 实例化formatter  
handler.setFormatter(formatter)      # 为handler添加formatter  
  
logger = logging.getLogger('viabtc')    # 获取名为viabtc的logger  
logger.addHandler(handler)           # 为logger添加handler  
logger.setLevel(logging.DEBUG)  

#定投策略
def do_strategy():
    if check_balance() :
        logger.info("Account Balance CNY [%.2f] BTC [%.2f] BCC [%.2f] ",Account['CNY'],Account['BTC'],Account['BCC'])
        logger.info("Market %s start Order [%s] ", const.ORDER_MARKET,const.ORDER_AMOUNT)
        result = trade_market_order(const.ORDER_MARKET,const.ORDER_TYPE_BUY,const.ORDER_AMOUNT)    
        if result and result['code'] == 0 :
            logger.info("Market %s order success amount [%s] avg_price [%s]", const.ORDER_MARKET,const.ORDER_AMOUNT,result['data']['avg_price'])
        else:
            logger.error("Market %s order amount [%s] failed", const.ORDER_MARKET,const.ORDER_AMOUNT)
while 1:
    do_strategy()
    time.sleep(const.ORDER_TIME_INTERVAL)

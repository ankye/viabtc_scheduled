
# viabtc_scheduled
viabtc btc bcc 定投脚本

下载脚本
```
git clone https://github.com/ankye/viabtc_scheduled
```
安装步骤

1. 去viabtc申请apikey
```
https://www.viabtc.com/apikey
```
修改viabtc_scheduled.py的config部分
```python
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
#定投类型 const.BTCCNY const.BCCCNY  const.BCCBTC
const.ORDER_MARKET = const.BCCCNY
#账户限额,保留一部分钱，账户达到最低限额就停止定投
# BTCCNY和BCCCNY  CNY账户
# BCCBTC          BTC账户
const.ACCOUNT_LIMIT = 1500
#定投间隔,单位秒, 
# 每分钟=60 每小时= 60*60  每天=24*60*60 每周=7*24*60*60 
const.ORDER_TIME_INTERVAL = 30
#最大交易价格，超过价格就跳过
#BTCCNY和BCCCNY  CNY
#BCCBTC  比值
const.MAX_ORDER_PRICE = 1000

#config end
#==============================================================
```
测试运行
```
python viabtc_scheduled.py
```
Linux或者Macos运行日志查看 
```
tail -f viabtc_scheduled.txt
```
后台运行在Linux和Macos
```
nohup python viabtc_scheduled.py &
```
'''
0 起源
美国《旧金山纪事报》曾做大猩猩选股实验。把各种股票代码写在一块纸板上，
让大猩猩向写有股票代码的纸板投标，用此方法让大猩猩挑选出5只股票。
然后用大猩猩挑选的股票组合与《华尔街日报》8位知名分析师精心挑选的5只比较，
结果是大猩猩与分析师选的收益率不相上下。
1 羊驼策略
甘肃卫视电视节目将大猩猩换成了羊驼来选股
2 算法策略
将股票按收益率排序，卖掉买入股中最差收益率的，加入未买股中收益率最高的

代码运行平台：JoinQuant：www.joinquant.com
'''
import random
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import scipy.stats as stats
import math

#股票池为所有沪深300的股票
stocks = get_index_stocks('000300.XSHG')
num = len(stocks)
set_universe(stocks)
set_commission(PerTrade(buy_cost=0.0008, sell_cost=0.0015, min_cost=5))
set_slippage(FixedSlippage(0))
#初始买入20只股票
num_of_stocks = 20
#每次更新时替换1只股票：看过回测结果之后，我觉得替换的股票越少收益越高
num_of_change=1
#计算1日收益率
period=1
#用一个列表来保存每天持有的股票代码
stockshold=[]
#判断参数输入是否符合条件，如果不符合，则重置为默认值
if num_of_stocks > num:
    log.info("Too large num_of_stocks")
    num_of_stocks = 20;
elif num_of_change > num_of_stocks:
    log.info("Too large num_of_change")
    num_of_stocks = 1;

'''
预处理数据，将没有数据的股票剔除，同时加入收益率
构成一个列索引为股票名，收益率一行的索引为‘return’的
dataframe，并返回这个dataframe
'''
def process():
    #取出每只股票period天的收盘价格
    stocks_info=history(period, 'id', 'close')
    #去除信息不全的数据
    stocks_info.dropna(axis=0, how='any', thresh=None)
    #取出昨天和period天之前的收盘价，计算收益率
    a1=list(stocks_info.iloc[0])
    a2=list(stocks_info.iloc[period-1])
    a1=np.array(a1)
    a2=np.array(a2)
    #用一个dataframe来保存所有股票的收益率信息
    stocks_return = DataFrame(a2/a1, columns=['return'], index=stocks_info.columns)
    stocks_info = stocks_info.T
    #把收益率的数据加到相应的列
    stocks_info = pd.concat([stocks_info, stocks_return], axis=1)
    #将股票信息安照收益率从大到小来存储
    stocks_info = stocks_info.sort(columns=['return'], ascending=[False])
    #返回处理好的dataframe
    return stocks_info

#股票入池
def BuyStocks(stocks_info, cash):
    #计算现在持有的股票数
    current_num = len(stockshold)
    stocks_info = stocks_info.T
    #将已持有的股票从股票池中剔除
    for i in range(0, current_num):
        if stockshold[i] in stocks_info.columns:
            del stocks_info[stockshold[i]]
    stocks_info=stocks_info.T
    #计算在每只股票上可以支付的现金
    if num_of_stocks-current_num>0:
        cash=cash/(num_of_stocks-current_num)
    for i in range(0,num_of_stocks-current_num):
        #取得股票当前的价格
        current_price = stocks_info['current_price'][i]
        #判断是否有价格数据
        if math.isnan(current_price)==False:
            #计算每只股票可以购买的数量
            num_of_shares = int(cash/current_price)
            if num_of_shares>0:
                order(stocks_info.index[i], +num_of_shares)
                log.info("buying %s"%(stocks_info.index[i]))
                #将购买的股票代码加到stockhold中
                stockshold.append(stocks_info.index[i])

#股票出池
def SellStocks(stocks_info):
    stocks_hold = DataFrame()
    current_num = len(stockshold)
    #用一个dataframe来保存持有的股票的信息
    for i in range(0, current_num):
        stocks_hold = pd.concat([stocks_hold, stocks_info.loc[stockshold[i]]], axis=1)
    stocks_hold = stocks_hold.T
    #在持有的股票数不为0时，将持有的股票信息按照收益率大小从小到大排序
    if current_num > 0:
        stocks_hold = stocks_hold.sort(columns = ['return'])
    #把收益率最低的股票卖空
    for k in range(0, min(num_of_change, current_num)):
        #判断是否停牌
        if stocks_hold['paused'][k] == 'False':
            order_target(stocks_hold.index[k], 0)
            log.info("Selling %s" %(stocks_hold.index[k]))
            #在stockshold中去除已经卖空的股票的信息
            stockshold.remove(stocks_hold.index[k])

#每个单位时间调用一次（如果按天回测，则每天调用一次；如果按分钟，则每分钟调用一次）
def handel_data(context, data):
    stocks_info = process()
    stocks_num = len(stocks_info.index)
    #用一个列表来保存所有股票是否停牌的信息
    pause = []
    for i in range(0, stocks_num):
        if data[stocks_info.index[i]].paused == True:
            pause.append('True')
        else:
            pause.append('False')
    #将列表转换成dataframe以便加入到stocks_info中
    pause = DataFrame(pause, columns=['paused'], index=stocks_info.index)
    stocks_info = pd.concat([stocks_info, pause], axis=1)
    #用一个列表来保存所有股票当前的价格信息
    currentprice = []
    for i in range(0, stocks_num):
        currentprice.append(data[stocks_info.index[i]].price)
    current_price = DataFrame(currentprice, columns=['current_price'], index=stocks_info.index)
    #将股票是否停牌，当前价格的信息添加到stocks_info中
    stocks_info = pd.concat([stocks_info, current_price], axis=1)
    #取得当前现金
    cash = context.portfolio.cash
    #执行卖出股票的函数
    SellStocks(stocks_info)
    #执行买入股票的函数
    BuyStocks(stocks_info, cash)
































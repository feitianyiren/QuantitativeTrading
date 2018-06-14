# -*- coding: utf-8 -*-

import tushare as ts
import os

def GetTodayAllQuotesData():
    fileName = 'D:/today_all_quotes.csv'
    allData = ts.get_today_all()#一次性获取当前交易所有的股票行情数据（如果是节假日，即为上一交易日）
    if os.path.exists(fileName):
        allData.to_csv(fileName, mode='a', index=True, header=None, encoding='utf_8_sig')
    else:
        allData.to_csv(fileName, index=True, encoding='utf_8_sig')

def GetRealTimeQuotes():
    fileName = "D:/realtime_quotes.csv"
    #获取全部股票代码
    stocksBasic = ts.get_stock_basics()
    stocks = stocksBasic.index.tolist()

    for stock in stocks:
        realtime = ts.get_realtime_quotes(stock)

        if os.path.exists(fileName):
            realtime.to_csv(fileName, mode='a', header=None, index=False)
        else:
            realtime.to_csv(fileName)

if __name__ == '__main__':
    GetTodayAllQuotesData()





















import talib
import numpy as np
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

def GetMA10():
    df = ts.get_k_data('600600')
    df['MA10_rolling'] = pd.rolling_mean(df['close'], 10)
    close = [float(x) for x in df['close']]
    #调用talib计算10日移动平均线的值
    df['MA_talib'] = talib.MA(np.array(close), timeperiod=10)
    df.tail(12)
    print(df)

def GetMACD():
    df = ts.get_k_data('600600')
    close = close = [float(x) for x in df['close']]
    # 调用talib计算指数移动平均线的值
    df["EMA12"] = talib.EMA(np.array(close), timeperiod=6)
    df["EMA26"] = talib.EMA(np.array(close), timeperiod=12)
    # 调用talib计算MACD指标
    df['MACD'], df['MACDsignal'], df['MACDhist'] = talib.MACD(np.array(close), fastperiod=6, slowperiod=12, signalperiod=9)
    df.tail(12)
    print(df)

def GetRSI():
    df = ts.get_k_data('600600')
    close = close = [float(x) for x in df['close']]
    df["RSI"] = talib.RSI(np.array(close), timeperiod=12)#RSI的天数一般是6,12,24
    df["MOM"] = talib.MOM(np.array(close), timeperiod=5)
    df.tail(12)
    print(df)

if __name__ == '__main__':
    #GetMACD()
    GetRSI()



































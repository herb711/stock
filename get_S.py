import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
import datetime


def get_MDD(code_close):
    '''
    以EMA1的参数为12日EMA2的参数为26日，DIF的参数为9日为例来看看MACD的计算过程
    1、计算移动平均值（EMA）
    12日EMA的算式为
    EMA（12）=前一日EMA（12）×11/13 + 今日收盘价×2/13
    26日EMA的算式为
    EMA（26）=前一日EMA（26）×25/27 + 今日收盘价×2/27
    2、计算离差值（DIF）
    DIF=今日EMA（12）－今日EMA（26）
    3、计算DIF的9日EMA
    根据离差值计算其9日的EMA，即离差平均值，是所求的MACD值。为了不与指标原名相混淆，此值又名
    DEA或DEM。
    今日DEA（MACD）= 前一日DEA×8/10 + 今日DIF×2/10。
    计算出的DIF和DEA的数值均为正值或负值。
    用（DIF-DEA）×2即为MACD柱状图。
    '''

    DIF = []
    DEA = []
    MACD = []
    EMA12 = 0
    EMA26 = 0
    DIF9 = 0
    for i in code_close:
        e12 = EMA12*11/13 + i*2/13
        EMA12 = e12
        e26 = EMA26*25/27 + i*2/27
        EMA26 = e26
        ema = e12-e26
        DIF.append(ema)
        
        d9 = DIF9*8/10 + (ema)*2/10
        DIF9 = d9
        DEA.append(DIF9)
        
        MACD.append((DIF9-ema))
    '''
    plt.figure()
    plt.plot(DIF)
    plt.plot(DEA)
    plt.plot(MACD)
    plt.grid()
    plt.show()   
    '''
    
    return DIF, DEA, MACD


def get_stock(code,setdf):
    
    i = 0
    set_year = setdf[i] # 当前的年
    i += 1
    set_month = setdf[i] # 当前的月
    i += 1
    set_date = setdf[i] # 当前的日
    i += 1
    set_back = int(setdf[i]) # 回退的天数
    i += 1
    set_month_date = setdf[i] # 时间的分辨率 0月  1日
 
    # 设置要获取的股票的时间段
    date_end = datetime.datetime(int(set_year), int(set_month), int(set_date))
    date_start = (date_end + datetime.timedelta(days=set_back)).strftime("%Y-%m-%d") #往前2年数据
    date_end = date_end.strftime("%Y-%m-%d")
    
    #使用平安银行的数据
    # open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
    stock = ts.get_hist_data(code, start=date_start, end=date_end)  
    
    # 判断stock的长度
    code_size = len(stock)
    print(code_size)
    
    #打印头和尾部数据
    '''
    #print(len(stock))
    #print(stock.head(1))
    #print(stock.tail(1))
    '''       
    
    stock = stock.sort_index(0)  # 将数据按照日期排序下。
    code_ma5 = pd.Series(stock["ma5"].values) # k线
    code_close = pd.Series(stock["close"].values) # 收盘价
    code_low = pd.Series(stock["low"].values) # 最低价
    code_high = pd.Series(stock["high"].values) # 最高价
    code_vomule = pd.Series(stock["volume"].values) # 成交价
    
    code_DIFF, code_DEA, code_MACD = get_MDD(code_close)
    
    return code_vomule, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD
    
if __name__=="__main__":
    # 读取设置参数
    mydf = pd.read_csv('set.csv')
    
    setdf = mydf["设置参数"].values
    setcode = mydf["股票代码"].values
        
    #假设股票数据
    code = "600516"
    
    code_vomule, code_close, code_low, code_high = get_stock(code,setdf)
    
    
    
    
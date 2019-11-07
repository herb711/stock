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

'''
根据5日线、10日线、20日线、
来计算 40日线、60日线
滑动平均求k线图的 MA5，MA10，MA40，MA60
'''
def get_MA60(ma20):
    code_ma60 = []
    for i in range(len(ma20)):
        j60 = i + 3
        if j60 < len(ma20):
            code_ma60.append(np.mean(ma20[i:j60]))
    
    # 如果60日线一个数据都没有
    if len(code_ma60) <= 0:
        code_ma60.append(np.mean(ma20))
        
    # 将缺省部分进行填充
    for i in range(len(ma20)-len(code_ma60)):
        code_ma60.insert(0, code_ma60[0]) # 在最前面插入
    
    return code_ma60

'''
date：日期
open：开盘价
high：最高价
close：收盘价
low：最低价
volume：成交量
price_change：价格变动
p_change：涨跌幅
ma5：5日均价
ma10：10日均价
ma20:20日均价
v_ma5:5日均量
v_ma10:10日均量
v_ma20:20日均量
turnover:换手率[注：指数无此项]
'''

def get_stock(code,setdf):
    
    i = 0
    set_year = setdf[i] # 当前的年
    i += 1
    set_month = setdf[i] # 当前的月
    i += 1
    set_date = setdf[i] # 当前的日
    i += 1
    set_day = setdf[i] # 时间的分辨率  0日 1周 2月
    i += 1
    set_back = int(setdf[i]) # 回退的个数

    # 设置要获取的股票的时间段
    date_end = datetime.datetime(int(set_year), int(set_month), int(set_date))
    date_start = (date_end + datetime.timedelta(days=set_back)).strftime("%Y-%m-%d") #往前2年数据
    date_end = date_end.strftime("%Y-%m-%d")
    
    #使用平安银行的数据
    # open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
    #stock = ts.get_hist_data(code, start=date_start, end=date_end) 
    dataFrame_day = ts.get_hist_data(code) # 提取全部的数据 
    
    # 判断stock的长度
    code_size = len(stock)
    print(code_size)
    
    #打印头和尾部数据
    '''
    #print(len(stock))
    #print(stock.head(1))
    #print(stock.tail(1))
    '''     
    
    
    # 按时间分辨率进行选择
    if set_day == 2:
        stock = dataFrame_day
    elif set_day == 1:
        stock = dataFrame_day
    elif set_day == 0:
        stock = dataFrame_day
    #print(stock.info())


    # 按照日期进行数据切割
    stock = stock.sort_values(by="年月日") # 按日期进行排序
    date_end = datetime.datetime(int(set_year), int(set_month), int(set_date))
    date = stock['年月日'].values
    date = pd.to_datetime([str(i) for i in date])
    x = 0
    for index, d in enumerate(date):
        if d >= date_end:
            x = index
            break
    stock = stock[:x] # 要求日期必须是按从小到大的顺序排列
    


    code_ma20 = stock["ma20"].values
    code_close = stock["close"].values # 收盘价
    code_low = stock["low"].values # 最低价
    code_high = stock["high"].values # 最高价
    #code_J = stock["J"].values # KDJ
    code_vomule = pd.Series(stock["volume"].values) # 成交价
    
    code_ma20 = np.array(code_ma20,'float') 
    code_close = np.array(code_close,'float') 
    code_low = np.asarray(code_low,'float') 
    code_high = np.asarray(code_high,'float')
    #code_J = np.asarray(code_J,'float') 
    
    code_ma20 = code_ma20.tolist() 
    code_close = code_close.tolist() 
    code_low = code_low.tolist() 
    code_high = code_high.tolist()
    #code_J = code_J.tolist() 
    
    code_ma60 = get_MA60(code_ma20)
    
    code_DIFF, code_DEA, code_MACD = get_MDD(code_close)
    
    return code_ma60, code_low, code_J


    
if __name__=="__main__":
    # 读取设置参数
    mydf = pd.read_csv('set.csv')
    mydf = mydf.where(mydf.notnull(), None) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    #假设股票数据
    code = "600077"
    
    code_ma60, code_low, code_J = get_stock(code,setdf)
    print(code_ma60,code_low,code_J)
    
    
    
    
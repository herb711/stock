import os
import pandas as pd
import numpy as np
import datetime
import GetData_csv
import GetLongData



'''
根据收盘价来计算 5日线、10日线、20日线、40日线、60日线
滑动平均求k线图的 MA5，MA10，MA40，MA60
'''
def get_MA60(code_close):
    code_ma60 = []
    code_ma40 = []
    code_ma20 = []
    code_ma10 = []
    code_ma5 = []
    
    for i in range(len(code_close)):
        j60 = i + 60
        if j60 < len(code_close):
            code_ma60.append(np.mean(code_close[i:j60]))
        j40 = i + 40
        if j40 < len(code_close):
            code_ma40.append(np.mean(code_close[i:j40]))
        j20 = i + 20
        if j20 < len(code_close):
            code_ma20.append(np.mean(code_close[i:j20]))
        j10 = i + 10
        if j10 < len(code_close):
            code_ma10.append(np.mean(code_close[i:j10]))
        j5 = i + 5
        if j5 < len(code_close):
            code_ma5.append(np.mean(code_close[i:j5]))
    
    # 如果60日线一个数据都没有
    if len(code_ma60) < 1:
        code_ma60.append(np.mean(code_close))
    if len(code_ma40) < 1:
        code_ma40.append(np.mean(code_close))
    if len(code_ma20) < 1:
        code_ma20.append(np.mean(code_close))
    if len(code_ma10) < 1:
        code_ma10.append(np.mean(code_close))
    if len(code_ma5) < 1:
        code_ma5.append(np.mean(code_close))
        
    # 将缺省部分进行填充，在最前面插入
    for i in range(len(code_close)-len(code_ma60)):
        code_ma60.insert(0, code_ma60[0])
    for i in range(len(code_close)-len(code_ma40)):
        code_ma40.insert(0, code_ma40[0])
    for i in range(len(code_close)-len(code_ma20)):
        code_ma20.insert(0, code_ma20[0])
    for i in range(len(code_close)-len(code_ma10)):
        code_ma10.insert(0, code_ma10[0])
    for i in range(len(code_close)-len(code_ma5)):
        code_ma5.insert(0, code_ma5[0])
    
    return code_ma60, code_ma40, code_ma20, code_ma10, code_ma5

def changedata(s,stock):
    d = stock[s].values    
    d = np.array(d,'float')    
    d = d.tolist() 
    return d

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
    set_back = int(abs(setdf[i])) # 回退的个数
    
    if set_year == 0:
        set_year = 1999
    if set_month == 0:
        set_month = 1
    if set_date == 0:
        set_date = 1
        
    date_end = datetime.datetime(int(set_year), int(set_month), int(set_date))

    # 判断文件夹是否存在
    file_path = r"C:\FTP\Stage11\stock_data"
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    # 获取数据
    code_dir_day = "C:\FTP\Stage11\stock_data\day_"+str(code)+".csv"
    code_dir_week = "C:\FTP\Stage11\stock_data\week_"+str(code)+".csv"
    code_dir_month = "C:\FTP\Stage11\stock_data\month_"+str(code)+".csv"
    
    code_download = False
    if int(set_year) > 1999:# 有具体时间，从本地数据中进行查询
        # 判断文件是否存在
        if os.path.exists(code_dir_day) and os.path.exists(code_dir_week) and os.path.exists(code_dir_month):
            # 时间判断
            t = os.path.getmtime(code_dir_day) # 获取文件的修改时间 
            t = datetime.datetime.fromtimestamp(t) # 格式转换
            if date_end > t: #如果文件存在的时间小于设定的搜索时间，重新爬取数据
                code_download = True
        else: # 文件不存在，重新搜寻数据
            code_download = True
    else:# 小于等于1999时，直接爬取数据
        code_download = True
    
    if code_download == True:
        dataFrame_day,dataFrame_week,dataFrame_month = GetLongData.Start(code)
        dataFrame_day.to_csv(code_dir_day, encoding='utf-8-sig')
        dataFrame_week.to_csv(code_dir_week, encoding='utf-8-sig')
        dataFrame_month.to_csv(code_dir_month, encoding='utf-8-sig')
    else:
        dataFrame_day = pd.read_csv(code_dir_day)
        dataFrame_week = pd.read_csv(code_dir_week)
        dataFrame_month = pd.read_csv(code_dir_month)

    # 按时间分辨率进行选择
    if set_day == 2:
        stock = dataFrame_month
    elif set_day == 1:
        stock = dataFrame_week
    elif set_day == 0:
        stock = dataFrame_day
    #print(stock.info())
        
    stock = stock.sort_values(by="年月日") # 按日期进行排序

    # 计算60日线等
    code_close = stock["收"].values # 收盘价
    code_ma60, code_ma40, code_ma20, code_ma10, code_ma5 = get_MA60(code_close)
    
    ma = pd.DataFrame({'code_ma60':code_ma60,'code_ma40':code_ma40,'code_ma20':code_ma20,'code_ma10':code_ma10,'code_ma5':code_ma5})
    stock = pd.concat([stock, ma], axis=1) #加入到数据中    
    
    # 按照日期进行数据切割
    if int(set_year) > 1999: # 日期设置为1999时，日期剪切不起作用
        date = stock['年月日'].values
        date = pd.to_datetime([str(i) for i in date])
        x = len(date)
        for index, d in enumerate(date):
            if d >= date_end:
                x = index
                break
        stock = stock[:x] # 要求日期必须是按从小到大的顺序排列
    # 控制数据段长度
    if len(stock) > set_back:# 当整体数据长度大于回退个数时，进行删减
        x = len(stock) - set_back
        stock = stock[x:]
        
    #x = stock.loc[:,['收']].values
    code_deal = changedata("成交量",stock) # 成交价
    code_close = changedata("收",stock) # 收盘价
    code_low = changedata("低",stock)   # 最低价
    code_high = changedata("高",stock)  # 最高价   
    code_DIFF = changedata("DIFF",stock)
    code_DEA = changedata("DEA",stock)
    code_MACD = changedata("MACD",stock)
    code_ma60 = changedata("code_ma60",stock)
    code_ma40 = changedata("code_ma40",stock)
    code_ma20 = changedata("code_ma20",stock)
    code_ma10 = changedata("code_ma10",stock)
    code_ma5 = changedata("code_ma5",stock)
        
    return code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD, [code_ma60, code_ma40, code_ma20, code_ma10, code_ma5]
    
if __name__=="__main__":
    mydf = pd.read_excel('C:\stage11\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
        
    #假设股票数据
    code = "600516"    
    
    get_stock(code,setdf)
    
    
    
    
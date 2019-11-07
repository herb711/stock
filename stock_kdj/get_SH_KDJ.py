import os
import pandas as pd
import numpy as np
import datetime
import pandas as pd
import numpy as np

import GetKDJData
import GetKDJData_csv

'''
获取股票数据

'''



'''
根据收盘价来计算 40日线、60日线
滑动平均求k线图的 MA5，MA10，MA40，MA60
'''
def get_MA60(code_close):
    code_ma60 = []
    code_ma20 = []
    for i in range(len(code_close)):
        j60 = i + 60
        if j60 < len(code_close):
            code_ma60.append(np.mean(code_close[i:j60]))
            
        j20 = i + 20
        if j20 < len(code_close):
            code_ma20.append(np.mean(code_close[i:j20]))
    
    # 如果60日线一个数据都没有
    if len(code_ma60) < 1:
        code_ma60.append(np.mean(code_close))
    if len(code_ma20) < 1:
        code_ma20.append(np.mean(code_close))
        
    # 将缺省部分进行填充
    for i in range(len(code_close)-len(code_ma60)):
        code_ma60.insert(0, code_ma60[0]) # 在最前面插入
        
    # 将缺省部分进行填充
    for i in range(len(code_close)-len(code_ma20)):
        code_ma20.insert(0, code_ma20[0]) # 在最前面插入
    
    return code_ma60, code_ma20



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
    
    if set_year == 0:
        set_year = 1999
    if set_month == 0:
        set_month = 1
    if set_date == 0:
        set_date = 1
        
    date_end = datetime.datetime(int(set_year), int(set_month), int(set_date))

    # 判断文件夹是否存在
    file_path = "C:\FTP\Stage10\stock_data"
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    # 获取数据        
    code_dir_day = "C:\FTP\Stage10\stock_data\day_"+str(code)+".csv"
    code_dir_week = "C:\FTP\Stage10\stock_data\week_"+str(code)+".csv"
    
    code_download = False
    if int(set_year) > 1999:# 有具体时间，从本地数据中进行查询
        # 判断文件是否存在
        if os.path.exists(code_dir_day) and os.path.exists(code_dir_week):
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
        dataFrame_day, dataFrame_week = GetKDJData.Start(code)
        dataFrame_day.to_csv(code_dir_day, encoding='utf-8-sig')
        dataFrame_week.to_csv(code_dir_week, encoding='utf-8-sig')
    else:
        dataFrame_day = pd.read_csv(code_dir_day)
        dataFrame_week = pd.read_csv(code_dir_week)
     
    #dataFrame_day, dataFrame_week = GetKDJData_csv.getstock(code)
    
    # 按时间分辨率进行选择
    if set_day == 2:
        stock = dataFrame_week
    elif set_day == 1:
        stock = dataFrame_week
    elif set_day == 0:
        stock = dataFrame_day
    #print(stock.info())
    
    stock = stock.sort_values(by="年月日") # 按日期进行排序
    # 按照日期进行数据切割
    if int(set_year) > 1999: # 小于等于1999时，日期剪切不起作用
        date = stock['年月日'].values
        date = pd.to_datetime([str(i) for i in date])
        x = len(date)
        for index, d in enumerate(date):
            if d >= date_end:
                x = index
                break
        stock = stock[:x] # 要求日期必须是按从小到大的顺序排列

    code_ma30 = stock["MA30"].values
    code_close = stock["收"].values # 收盘价
    code_low = stock["低"].values # 最低价
    code_high = stock["高"].values # 最高价
    code_J = stock["J"].values # KDJ
    
    code_ma30 = np.array(code_ma30,'float') 
    code_close = np.array(code_close,'float') 
    code_low = np.asarray(code_low,'float') 
    code_high = np.asarray(code_high,'float')
    code_J = np.asarray(code_J,'float') 
    
    code_ma30 = code_ma30.tolist() 
    code_close = code_close.tolist() 
    code_low = code_low.tolist() 
    code_high = code_high.tolist()
    code_J = code_J.tolist() 
    
    # 计算ma60
    code_ma60, code_ma20 = get_MA60(code_close)
    
    return code_low, code_J, code_ma60, code_ma20
    
if __name__=="__main__":
    # 读取设置参数
    mydf = pd.read_csv('set.csv')
    mydf = mydf.where(mydf.notnull(), None) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    #假设股票数据
    code = "002039"
    print(os.getcwd())
    code_low, code_J, code_ma60, code_ma20 = get_stock(code,setdf)
    print(code_ma60,code_low,code_J)
    
    
    
    
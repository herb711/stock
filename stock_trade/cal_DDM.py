# Coding = UTF-8
'''
判定
DEA
DIFF
MACD
在半年或1年内是否在0轴附近
0轴附近有一个浮动的范围，单独可调
'''
import pandas as pd
import heapq
import numpy as np
import matplotlib.pyplot as plt


'''
搜寻粘连---将连续处于0轴附近的数据段记录下来
data[code_DIFF, code_DEA, code_MACD]
area[0] #DIFF中轴浮动范围
area[1] #DEA中轴浮动范围
area[2] #MACD中轴浮动范围

返回所有符合条件的数据段的长度
'''
def wave_analyze(data, area):
    wave = []
    left = 0
    right = 0
    n = len(data[0])
    for i in range(n):
        right = i
        good = 0
        for j in range(3):
            x = data[j][i] # 循环3次，分别取出当前[code_DIFF, code_DEA, code_MACD]的值，判断是否在中轴附近浮动
            if x<area[j] and x>(-1*area[j]):
                good = good +1
        if good<3 :# 不符合条件
            if (right-left)>1 : #左右之间存在一定长度，记录在wave内
                wave.append(right-left)
            left = i
        elif i == n-1:
            wave.append(right-left) # 最后一个

    # 将所有符合条件的数据段的长度累加起来
    length = 0
    for i in wave:
        length = length + i
    
    return length


'''
搜寻粘连---在一定时间段内是否都处于0轴附近活动
'''
def MDD_analyze(data, area, scope):

    good = 0
    result = []
    for i in range(len(data[0,:])):
        if i+area > len(data[0,:]):
            break;
        for j in range(3):
            x = data[j, i:i+area]
            #搜索出范围内的最大的1个值
            wave_max = heapq.nlargest(1, x)
            #搜索出范围内的最小的1个值
            wave_min = heapq.nsmallest(1, x)
            
            # 当最大最小都在0轴的浮动范围以内，即最大小于0.1，最小大于-0.1，0.1可调
            if np.array(wave_max)<scope[j] and np.array(wave_min)>(-1*scope[j]):
                good = good + 1
        
        if good > 2: # 三条线都符合条件
            result.append([i,i+area])
        
        good = 0 # 重新置零
    
    return result


if __name__=="__main__":
    # 读取设置参数
    mydf = pd.read_excel('C:\stage11\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    import get_SH
    code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD, code_ma = get_SH.get_stock('601360',setdf)

    wave = wave_analyze(np.array([code_DIFF, code_DEA, code_MACD]), [0.5, 0.5, 0.5])       

    plt.figure(figsize=(16,8))
    plt.plot(code_DIFF)
    plt.plot(code_DEA)
    plt.plot(code_MACD)

    print(wave)
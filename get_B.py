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

def MDD_analyze(data, area, scope):
    #data = get_MDD(data)
    
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
        
        good = 0
    
    return result


if __name__=="__main__":
    stock = pd.read_csv('result.csv')
    code_close = pd.Series(stock["收"].values) # 收盘价
    result = MDD_analyze(code_close, 6, [0.3, 0.4, 0.3])  # 6个点半年，后面3个为判定幅度和数据顺序一致
    print(result)    
    
    #将原始数据和波峰，波谷画到一张图上
    m = np.zeros(len(result))
    plt.figure()
    plt.plot(arr[:,0])
    plt.plot(arr[:,1])
    plt.plot(arr[:,2])
    plt.plot(result, m, 'ro')#红色的点
    plt.grid()
    plt.show()    

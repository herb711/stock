'''
k线图

5日线是白色

10日线是黄色

20日线是紫色

60日线是绿色

'''

import pylab as plt
import pandas as pd
import numpy as np

'''
根据收盘价来计算5日线、10日线、40日线、60日线
滑动平均求k线图的 MA5，MA10，MA40，MA60
'''
def get_k(code_close):
    code_ma5 = []
    code_ma10 = []
    code_ma40 = []
    code_ma60 = []
    for i in range(len(code_close)):
        j5 = i+5
        j10 = i+10
        j40 = i+40
        j60 = i+60
        if j5 < len(code_close):
            code_ma5.append(np.mean(code_close[i:j5]))
        if j10 < len(code_close):
            code_ma10.append(np.mean(code_close[i:j10]))
        if j40 < len(code_close):
            code_ma40.append(np.mean(code_close[i:j40]))
        if j60 < len(code_close):
            code_ma60.append(np.mean(code_close[i:j60]))
    
    # 判断数据量是否足够
    if len(code_ma60) <= 0:
        code_ma60.append(np.mean(code_close))
        
    # 将缺省部分进行填充
    for i in range(len(code_close)-len(code_ma5)):
        code_ma5.insert(0, code_ma5[0])
    for i in range(len(code_close)-len(code_ma10)):
        code_ma10.insert(0, code_ma10[0])
    for i in range(len(code_close)-len(code_ma40)):
        code_ma40.insert(0, code_ma40[0])
    for i in range(len(code_close)-len(code_ma60)):
        code_ma60.insert(0, code_ma60[0])
    
    return code_ma5,code_ma10,code_ma40,code_ma60

def get_k60(code_close,time):
    j60 = 0
    if time == 0: # 日
        j60 = 60
    elif time == 1: # 周
        j60 = 9
    elif time == 2: # 月
        j60 = 2
        
    code_ma60 = []
    for i in range(len(code_close)):
        if j60 < len(code_close):
            code_ma60.append(np.mean(code_close[i:i+j60]))
    
    # 判断数据量是否足够
    if len(code_ma60) <= 0:
        code_ma60.append(np.mean(code_close))
        
    # 将缺省部分进行填充
    for i in range(len(code_close)-len(code_ma60)):
        code_ma60.insert(0, code_ma60[0])
    
    return code_ma60


'''
data = [code_ma60, code_ma40, code_ma20, code_ma10, code_ma5]
寻找4条线交叉的区域
该方法:
首先，将每一条线上的某一个点，去跟其余线上的每一个点做比较，找出交叉
然后，计算这一区间的最大值和最小值，要求不能超过设置范围
'''
def k_analyze(data,area):
    code_ma = [data[4],data[3],data[1],data[0]]
    
    cross = []
    i = 0
    # 判断是否有交叉
    for _ in range(len(code_ma[0])-int(area[0])):        
        # 区域滑动搜索
        width = i+int(area[0])
        a=b=c=d=e=0
        
        # 判断整体的最大距离
        x = []
        # 将4根线的数据组合起来
        for j in range(4): 
            x = x + code_ma[j][i:width]
        
        if len(x) > 1:
            # 求区间里的最大值和最小值
            xmax = max(x)
            xmin = min(x)
            if abs(xmax-xmin)<area[1]:
                e = 1

        # 判断是否有交叉
        for j in range(4): 
            # 查询当前线和其余3条线是否有交集
            for k in code_ma[j][i:width]: # 获得当前线段的某一个值
                # 将其余三条线的每一个值跟当前值进行比对
                for m in range(3):
                    for n in code_ma[m][i:width]: 
                        if abs(k-n) < 0.1: 
                            # 找到一个交集
                            if j == 0:
                                a = 1
                            if j == 1:
                                b = 1
                            if j == 2:
                                c = 1
                            if j == 3:
                                d = 1
        
        # 存储区间
        if a==1 and b==1 and c==1 and d==1 and e==1: 
            # 记录当前区域
            cross.append([i,width])
            i = width
        else:
            i = i+1
    
    # 整合区间
    result = []
    if (len(cross)>0):
        left = cross[0][0]
        right = cross[0][1]
        for i in range(len(cross)-1):
            if cross[i][1] != cross[i+1][0] :
                right = cross[i][1]
                result.append([left,right])
                left = cross[i+1][0]
                
    return result

'''
data = [code_ma60, code_ma40, code_ma20, code_ma10, code_ma5]
# 判断4均线有无交叉, 然后判断最低价是否在 k60之下 
'''
def k60_analyze(data,low,area):
    ma60 = data[0]
    
    cross = k_analyze(data, area) #判断4均线有无交叉
    
    # 只要有一个部分是交叉的，就认为交叉，后面需要根据时间段来进行判断
    ok = False
    for i in range(len(cross)):
        left = cross[i][0]
        right = cross[i][1]
        x1 = min(ma60[left:right])
        x2 = min(low[left:right])
        if x1 > x2:
            ok = True
    return ok


# 仅判断最低价是否在 K60 之下
def K60_down(ma60, low, left, down):
    # 没有波
    if left == -1: 
        return False
    # left的长度超过ma60
    if len(ma60)<left or len(low)<left:
        return False
    # 没有数据
    if len(ma60)==0 or len(low)==0:
        return False    

    ok = False
    x1 = min(ma60[left:])
    x1 = x1 + x1 * down # 增加一定比例的范围，默认20%
    x2 = max(low[left:])
    if x1 > x2:
        ok = True
    return ok
        


if __name__=="__main__":
    # 读取设置参数
    mydf = pd.read_excel('C:\stage11\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    import get_SH
    code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD, code_MA60 = get_SH.get_stock('600776',setdf)

    plt.figure(figsize=(16,8))
    plt.plot(code_MA60[0])
    plt.plot(code_MA60[1])
    #plt.plot(code_MA60[2])
    plt.plot(code_MA60[3])
    plt.plot(code_MA60[4])

    C_ok = k60_analyze(code_MA60,code_low,[3, 0.2]) # K线粘黏时间范围（搜寻长度），K线粘黏高度范围（搜寻高度）
    print(C_ok)














'''


        
# 找交叉
def k_analyze4(site,area,scope):

    one,two,three,four = get_k(site)
    
    price=[]
    idx=[]
    for i in np.arange(area,len(site),1):
        a=b=c=d=e=f=0
        for j in np.arange(i-area,i,1):
            if abs(one[j]-two[j])<scope :a=1
            if abs(three[j]-two[j])<scope:b=1
            if abs(one[j]-three[j])<scope:c=1
            if abs(one[j]-four[j])<scope:d=1
            if abs(two[j]-four[j])<scope:e=1
            if abs(three[j]-four[j])<scope:f=1
            
            if a==1 and b==1 and c==1 and d==1 and e==1 and f==1: 
                price.append([i-area,i])
                break
    
    
    # 将粘黏的点拼接起来
    x=price[0][0]
    y=price[0][1]
    for i in np.arange(len(price)):
        if not i==len(price)-1:
            if price[i][0]+1==price[i+1][0]:
                y=price[i+1][1]
            else:
                idx.append([x,y])
                x=price[i+1][0]
                y=price[i+1][1]
            continue
        idx.append([x,y])

    return idx

                
        amin = []
        amin.append(min(code_ma5[i:i+area[0]]))
        amin.append(min(code_ma10[i:i+area[0]]))
        amin.append(min(code_ma40[i:i+area[0]]))
        amin.append(min(code_ma60[i:i+area[0]]))
        amax = []
        amax.append(max(code_ma5[i:i+area[0]]))
        amax.append(max(code_ma10[i:i+area[0]]))
        amax.append(max(code_ma40[i:i+area[0]]))
        amax.append(max(code_ma60[i:i+area[0]]))
        
        nmin = np.array(amin)
        vmin = np.var(nmin)
        nmax = np.array(amax)
        vmax = np.var(nmax)
        
        if vmin<area[1] or vmax<area[1] :
            result.append([i,i+area[0]])
'''


'''
k_analyze1
该方法是将每一条线上的某一个点，去跟其余线上的每一个点做比较
该方法，能够找出交叉
问题：如果线段是 2根 和 2根 相互交叉，但是2对之间又相隔很远，这种情况有交叉，但是不符合
'''
def k_analyze1(data,area):
    code_ma = get_k(data)
    
    cross = []
    i = 0
    # 判断是否有交叉
    for _ in range(len(code_ma[0])-area[0]):        
        # 区域滑动搜索
        width = i+area[0]
        a=b=c=d=0
        
        # 当前区域进行搜索，4条线遍历
        for j in range(4): 
            # 查询当前线和其余3条线是否有交集
            for k in code_ma[j][i:width]: # 获得当前线段的某一个值
                # 将其余三条线的每一个值跟当前值进行比对
                for m in range(3):
                    for n in code_ma[m][i:width]: 
                        if abs(k-n) < area[1]: 
                            # 找到一个交集
                            if j == 0:
                                a = 1
                            if j == 1:
                                b = 1
                            if j == 2:
                                c = 1
                            if j == 3:
                                d = 1
        if a==1 and b==1 and c==1 and d==1: 
            # 记录当前区域
            cross.append([i,width])
            i = width
        else:
            i = i+1
    
    # 整合区间
    result = []
    if (len(cross)>0):
        left = cross[0][0]
        right = cross[0][1]
        for i in range(len(cross)-1):
            if cross[i][1] != cross[i+1][0] :
                right = cross[i][1]
                result.append([left,right])
                left = cross[i+1][0]
                
    return result

'''
k_analyze
计算这一区间的最大值和最小值
限制：因为是求整个区间的最大值和最小值范围不能太大
'''
def k_analyze2(data,area):
    code_ma = get_k(data)
    
    cross = []
    i = 0
    # 判断是否有交叉
    for _ in range(len(code_ma[0])-area[0]-1):        
        # 区域滑动搜索
        width = i+area[0]
        x = []
        # 将4根线的数据组合起来
        for j in range(4): 
            x = x + code_ma[j][i:width]
        
        if len(x) > 1:
            # 求区间里的最大值和最小值
            xmax = max(x)
            xmin = min(x)
            if abs(xmax-xmin)<area[1]:
                cross.append([i,width])
                i = width
            else:
                i = i+1        
    
    # 整合区间
    result = []
    if (len(cross)>0):
        left = cross[0][0]
        right = cross[0][1]
        for i in range(len(cross)-1):
            if cross[i][1] != cross[i+1][0] :
                right = cross[i][1]
                result.append([left,right])
                left = cross[i+1][0]
                
    return result
'''
k线图

5日线是白色

10日线是黄色

20日线是紫色

60日线是绿色

'''

import pylab as pl
import pandas as pd
import numpy as np

'''
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

'''
k_analyze
该方法:
首先，将每一条线上的某一个点，去跟其余线上的每一个点做比较，找出交叉
然后，计算这一区间的最大值和最小值，要求不能超过设置范围
'''
def k_analyze(data,area):
    code_ma = get_k(data)
    
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


# 判断最低价是否在 k60之下
def k60_analyze(data,low,area):
    
    ma60 = get_k(data)[3]
    
    cross = k_analyze(data, area)
    
    ok = False
    for i in range(len(cross)):
        left = cross[i][0]
        right = cross[i][1]
        x1 = min(ma60[left:right])
        x2 = min(low[left:right])
        if x2 < x1:
            ok = True
    return ok


if __name__=="__main__":
    import get_S

    '''
    stock = pd.read_csv('result.csv')
    code_close = pd.Series(stock["收"].values) # 收盘价
    
    '''

    # 读取设置参数
    mydf = pd.read_csv('set.csv')
    setdf = mydf["设置参数"].values
    code = "600624"   # 复旦复华         
    code_vomule, code_close, code_low, code_high = get_S.get_stock(code, setdf)    
    
    
    result = k_analyze(code_close, [3, 0.2])  # 数据； 搜寻区间； 判定幅度；
    
    code_ma5,code_ma10,code_ma40,code_ma60 = get_k(code_close)
    #将原始数据和波峰，波谷画到一张图上
    m = np.zeros(len(result))
    pl.figure(figsize=(25,8))
    pl.plot(code_ma5)
    pl.plot(code_ma10)
    pl.plot(code_ma40)
    pl.plot(code_ma60)
    pl.plot(code_low)

    left = [] #波谷x
    right = [] #波谷y
    for i,j in result:
        left.append(i)
        right.append(j)
        
    pl.plot(left, m, 'ro')#红色的点
    pl.plot(right, m, 'go')#绿色的点
    pl.grid()
    pl.show()  
    
    ok = k60_analyze(code_close,code_low,[3, 0.2])
    
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
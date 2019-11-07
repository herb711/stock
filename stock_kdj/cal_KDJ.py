'''
根据KDJ寻找波峰波谷
'''


import matplotlib.pyplot as pl
import pandas as pd
import os
import get_SH_KDJ
import cal_MA
    
            
'''
area[0]倍大小进入波区，下降area[1]倍走出波区，area[2]波宽（波形宽度条件没有使用）
area[3]属于零值的高度判断（在何种情况下属于零位）
1 判断是否进入波区，在此期间不断更新最低点
2 进入波区后，判断是否走出波区
3 判断是否走出波区，使用的是下降到整体波形的80% 或 下降到area[0]倍
该方法的优势是能够较好的找到一个完整的波
缺陷是，如果波没有下降到整体的80%，就不会被识别，可以根据调整下降的比例来改变
'''
def wave_analyze(data, area):
    wave = []

    left = 0      # 波形左值点的位置
    middle = 0     # 波形最高值点的位置
    updown = 0
    
    for i in range(len(data)) :
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if data[left] > data[i] :
                left = i
            
            if data[i] > area[0] : # 按绝对值进行判断
                updown = 1 # 进入波区 
                middle = i
        
        elif updown == 1 : # 进入波区， 判断是否走出波区
            # 更新最大点的位置
            if data[middle] < data[i] :
                middle = i
                
            # 现在是在波区，当下降到指定高度以下时，认为走出波区
            if area[1] > data[i] :
                updown = 0 # 走出波区
                wave.append([left, middle, i]) # 记录波的左值，波峰，右值的位置
                left = i    
                
    if updown == 1: # 如果最后时刻还在波区，没有走出波区，不记录波
        wave = []
    else:
        if len(wave) > 0:
            wave = wave[-1] # 只使用最后一个波
        
    return wave #波的左值，波峰，右值的位置，以及波的大小


'''
找波，然后提取波形最后一部分的数据
'''
def wave_pick(data, area):
    wave = wave_analyze(data, area)  # 找波
    if len(wave) < 1:
        return -1
    
    right = wave[2] # 提取波形里的波形最右边的序号

    return right 


'''
判断从走出波区到最后时刻，是否一直维持在零点
'''
def wave_zero(data, area):
    
    wave = wave_analyze(data, area)  # 大于96进入波区，下降到10以下走出波区，稳定在0附件5日以上

    if len(wave)<1 or len(data)<1:
        return 0, 0

    middle = wave[1]
    right = wave[2] # 提取波形里的波形最右边的序号

    # 先判断是否超出了上行上限，然后再判断整体长度
    if len(data)<=right+1:
        x = data[-1] # right是最后一个数据时
        if x <= area[3]:
            n = 1
        else:
            n = 0
    else:
        x = data[right:] # 截取最后一段数据    
        if  max(x) <= area[3]:
            n = len(x)
        else:
            n = 0
    
    '''
    n = 1
    for k in x:
        if k < area[3]: 
            n += 1 #当值小于 area[3]即，主波上行上限时，累计长度
        else:
            break #当值小于 area[3]即，主波上行上限时，退出累计计数
    '''
            
    # 返回波峰位置和累计长度
    return middle, n
        


if __name__=="__main__":
    print(os.getcwd())
    '''
    #code_kdj = pd.Series(stock[["K","D","J"]].values) # kdj
    stock = pd.read_csv('test/600077_dayresult.csv')
    code_kdj = pd.Series(stock["J"].values) # kdj只分析J值
    '''
    
    # 参数读取
    num_v = 5 #成交量放大缩小倍数
    num_dif = num_v + 1 #DIFF中轴浮动范围
    num_dea = num_dif + 1 #DEA中轴浮动范围
    num_macd = num_dea + 1 #MACD中轴浮动范围
    num_kt = num_macd + 1 #K线粘黏时间范围（搜寻长度）
    num_kh = num_kt + 1 #K线粘黏高度范围（搜寻高度）
    num_k60down = num_kh + 1 #判断最低价是否在K60以下（比例）
    
    num_kdj_h = num_k60down +1   #KDJ主波高度上限 
    num_kdj_dABC = num_kdj_h +1  #KDJ主波下降区间ABC	0.1
    num_kdj_dD = num_kdj_dABC +1 #KDJ主波下降区间D	10
    num_kdj_dE = num_kdj_dD +1   #KDJ主波下降区间E	35
    num_kdj_uABC = num_kdj_dE +1 #KDJ主波上行上限ABC	3
    num_kdj_uD = num_kdj_uABC +1 #KDJ主波最后上行上限D	28
    num_kdj_h2 = num_kdj_uD + 1  #KDJ副波高度上限
    num_kdj_d2ABC = num_kdj_h2 +1  #KDJ副波下降区间ABC	0.1
    num_kdj_d2D = num_kdj_d2ABC +1 #KDJ副波下降区间D	10
    num_kdj_u2A = num_kdj_d2D +1   #KDJ副波上行上限A	2D
    num_kdj_u2B = num_kdj_u2A +1 #KDJ副波上行上限B	4
    num_kdj_u2C = num_kdj_u2B +1 #KDJ副波上行上限C	10
    num_kdj_u2D = num_kdj_u2C +1 #KDJ副波上行上限D	24

    # 读取设置参数
    mydf = pd.read_excel('C:\stage10\set.xls')
    mydf = mydf.where(mydf.notnull(), None) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    code_low, code_J, code_ma60, code_ma20 = get_SH_KDJ.get_stock('002103',setdf)

    r, n = wave_zero(code_J, [setdf[num_kdj_h],setdf[num_kdj_dE],1,999])
    k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])


    wave = wave_analyze(code_J, [setdf[num_kdj_h],setdf[num_kdj_dABC],1,setdf[num_kdj_uABC]])   # 大于96进入波区，下降到10以下走出波区，稳定在0附件5日以上
    print(wave)
    
    #将原始数据和波峰，波谷画到一张图上
    pl.figure()
    pl.plot(code_J)
    pl.show()  

    wave_base =[]
    wave_crest =[]
    '''
    for i,j,m in wave:
        wave_base.append([i,code_J[i]])
        wave_crest.append([j,code_J[j]])
    '''
    i = wave[0]
    j = wave[1]
    wave_base.append([i,code_J[i]])
    wave_crest.append([j,code_J[j]])

    wave_crest_x = [] #波峰x
    wave_crest_y = [] #波峰y
    for i,j in wave_crest:
        wave_crest_x.append(i)
        wave_crest_y.append(j)
  
    wave_base_x = [] #波谷x
    wave_base_y = [] #波谷y
    for i,j in wave_base:
        wave_base_x.append(i)
        wave_base_y.append(j)
    pl.plot(wave_base_x, wave_base_y, 'go')#绿色的点
    pl.plot(wave_crest_x, wave_crest_y, 'ro')#红色的点
        
    pl.grid()
    pl.show()  
    
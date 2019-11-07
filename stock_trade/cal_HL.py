'''
根据最高价和最低价寻找波峰波谷，采用方法3

方法1：
使用面积来寻找波
跟矩形面积相差不多的情况认为是有一个波

方法2：
使用同样的形状来（只有高度，没有宽度？）

方法3:
华驰逻辑法，跟成交量找波方法的区别在于，进入波区和退出波区，是按最低价的上浮百分比而定

'''

import matplotlib.pyplot as pl
import pandas as pd
            

'''
寻找波形
high最高价, low最低价
area：上升area[0]倍大小进入波区，下降需要回到最低点才走出波区，浮动area[1]，area[2]波宽（波形宽度条件没有使用）

1 判断是否进入波区，在此期间不断更新最低点
2 进入波区后，判断是否走出波区
3 判断是否走出波区，使用的是下降到整体波形的80% 或 下降到area[0]倍---该方法的优势是能够较好的找到一个完整的波，缺陷是，如果波没有下降到整体的80%，就不会被识别，可以根据调整下降的比例来改变
'''
def wave_analyze(high, low, area):
    # 将数据整体提升，避免有负数和零的情况***存在一个很大的问题，因为找波用的放大倍数因此直接拉升会影响比例关系，但是因为该值无负数，所以没问题
    x1 = min(high)
    x2 = min(low)
    x = min(x1,x2)
    if x <= 0:
        high = high + 1 + abs(x)
        low = low + 1 + abs(x)

    wave = []

    left = 0
    middle = 0     # 波形最高值点的位置
    updown = 0
    
    for i in range(len(low)) :
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if low[left] > low[i] :
                left = i
            if left == i: # 当前值就是最低点时，不进行比较
                continue
                    
            k_in = (area[0]+1) * low[left]
                
            if high[i] > k_in:# 判断是否放大额定倍数，用减法可以允许最小值为负数的情况
                updown = 1 # 进入波区 
                middle = i

        if updown == 1 : # 进入波区 
            # 更新最大点的位置
            if high[middle] < high[i] :
                middle = i

            # 选择走出波区的范围，x1是设置的条件，x2是作为保险条件
            x1 = (1+area[1]) * low[left]       # 最低点上浮6%
            x2 = min(high[middle]*0.06, k_in)  # 波高的6% 或 进入波区的高度  

            # 判断是否走出波区
            if high[i] < x1 :#or low[i] < x2 :# 针对最低点而言 或  针对波高而言
                updown = 0 # 走出波区
                # 此时的波的左值不一定准确，精确找波时，此时可重新更新左值
                
                # 记录波的信息
                wave.append([left, middle, i]) # 记录波的左值，波峰，右值的位置
                # 更新左值，重新找波
                left = i        
                
    return wave       


if __name__=="__main__":
    # 读取设置参数
    mydf = pd.read_excel('C:\stage11\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    import get_SH
    code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD, code_ma = get_SH.get_stock('600446',setdf)

    wave = wave_analyze(code_high, code_low, [0.6, 0.6, 1]) #6倍大小进入波区，下降到5倍走出波区，1是搜索的区域

    #将原始数据和波峰，波谷画到一张图上
    pl.figure(figsize=(25,8))
    pl.plot(code_high)
    pl.plot(code_low)

    wave_l =[]
    wave_m =[]
    wave_r =[]
    for i,m,j in wave:
        wave_l.append([i,code_low[i]])
        wave_m.append([m,code_high[m]])
        wave_r.append([j,code_low[j]])

    wave_crest_x = [] #波峰x
    wave_crest_y = [] #波峰y
    for i,j in wave_m:
        wave_crest_x.append(i)
        wave_crest_y.append(j)
  
    wave_base_x = [] #波谷x
    wave_base_y = [] #波谷y
    for i,j in wave_l:
        wave_base_x.append(i)
        wave_base_y.append(j)
    wave_base2_x = [] #波谷x
    wave_base2_y = [] #波谷y
    for i,j in wave_r:
        wave_base2_x.append(i)
        wave_base2_y.append(j)        
        
    pl.plot(wave_crest_x, wave_crest_y, 'ro')#红色的点
    pl.plot(wave_base_x, wave_base_y, 'go')#绿色的点
    pl.plot(wave_base2_x, wave_base2_y, 'bo')#绿色的点
    
    pl.grid()
    pl.show()  
    
'''


# 计算范围内的面积，以图像最左边的点为计算点
def area_analyze(high, left):
    # 求最高值和最左侧的最低值围成的面积
    area_h = 0
    right = 0
    for i in range(len(high)):
        right = i
        # 当遇到比最低点更低时，返回
        if left_v > high[i] :
            break
        area_h = area_h + high[i]-left_v

    return area_h, right





# 返回最大值和最小值，并且返回其所在序号
def maxmin_analyze(high, low):

    #list 的方法
    #print c.index(min(c)) # 返回最小值
    #print c.index(max(c)) # 返回最大值

    #low_min = heapq.nlargest(1, low)
    low_index = np.argmin(low)
    low_min = low[low_index]
    #high_max = heapq.nlargest(1, high)
    high_index = np.argmax(high)
    high_max = high[high_index]
    
    return low_min, low_index, high_max, high_index
    

    # 当遇到比最低点更低时，从新开始，更新最低点
    if left_v > high[i] :
        # 如果求得的面积大于现有面积，认为进入波区
        if area_h > area_o :
            wave.append()
        left_v = low[i]
        area_h = 0
            
'''
'''

        
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if low[left] > low[i] :
                left = i

            if low[left] == 0:
                k = area[0] # 如果出现为0的情况，基数默认为1
            else:
                k = abs(area[0]*low[left])
                
            if abs(high[i]-low[left]) >= k:# 判断是否放大额定倍数，用减法可以允许最小值为负数的情况
                updown = 1 # 进入波区 
                middle = i
                     
        if updown == 1 : # 进入波区 
            # 更新最大点的位置
            if high[middle] < high[i] :
                middle = i

            # 选择走出波区的范围
            if low[left] == 0:
                k1 = area[0] # 如果出现为0的情况，基数默认为1
                k2 = area[1]
            else:
                k1 = abs(area[0]*low[left])
                k2 = abs(area[1]*low[left])
                
            h = high[middle] - low[left]  # 计算当前的最大值和最低值的差距，即波高
            # 范围
            x1 = min(h*0.2, k1)  # 选波高的20% 或 进入波区的高度     当下降到离最低点很近时，退出波区
            x2 = max(h*0.8, k2)  # 选波高的80% 或 额定的下降距离     当下降到离最高点很远时，退出波区
            # 实际值
            if high[i] < low[left]: # 当前值低于最低点时，设置为-1，可退出波区
               y1 = -1 
            else:
               y1 = abs(high[i] - low[left])   # 当前值距离最低值的距离
            y2 = abs(high[middle] - low[i]) # 最高值距离当前值的距离
            
            # 判断是否走出波区
            if y1 < x1 or y2 > x2 :
                updown = 0 # 走出波区
                # 此时的波的左值不一定准确，精确找波时，此时可重新更新左值
                
                # 记录波的信息
                wave.append([left, middle, i]) # 记录波的左值，波峰，右值的位置
                # 更新左值，重新找波
                left = i             
'''
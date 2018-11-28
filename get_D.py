'''
根据最高价和最低价寻找波峰波谷


使用面积来寻找波
跟矩形面积相差不多的情况认为是有一个波

使用同样的形状来（只有高度，没有宽度？）
'''

import get_SH
import matplotlib.pyplot as pl
            
'''
# high最高价, low最低价, area窗口宽度、高度、下降比例 （波形宽度条件没有使用）
1 判断是否进入波区，在此期间不断更新最低点
2 进入波区后，判断是否走出波区
3 判断是否走出波区，使用的是下降到整体波形的80%，
该方法的优势是能够较好的找到一个完整的波
缺陷是，如果波没有下降到整体的80%，就不会被识别，可以根据调整下降的比例来改变
'''
def wave_analyze(high, low, area):
    wave = []

    left = 0
    right = 0
    updown = 0
    for i in range(len(low)) :
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if low[left] > low[i] :
                left = i
            
            if (high[i]/low[left]) > area[1] :
                updown = 1 # 进入波区 
                right = i
        
        if updown == 1 :
            # 更新最大点的位置
            if high[right] < high[i] :
                right = i

            h = high[right]/low[left]
            x = max(h*area[2],area[1])
            # 现在是上升，当下降到80%高度的时候，认为走出波区
            print(high[right],low[i], right, i)
            if (high[right]/low[i]) > x :
                updown = 0 # 走出波区
                wave.append([left, right, i, high[right]/low[i]]) # 记录波谷，波峰
                left = i
                              
    return wave       


if __name__=="__main__":
    code_vomule, code_close, code_low, code_high = get_SH.get_stock()
    
    wave = wave_analyze(code_high, code_low, [1, 2, 0.8])

    #将原始数据和波峰，波谷画到一张图上
    pl.figure()
    pl.plot(code_high)
    pl.plot(code_low)

    wave_base =[]
    wave_crest =[]
    for i,j,m,n in wave:
        wave_base.append([i,code_low[i]])
        wave_crest.append([j,code_high[j]])

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
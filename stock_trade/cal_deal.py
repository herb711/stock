'''
根据成交量寻找波峰波谷

方法:
华驰逻辑法，跟最低价最高价找波方法的区别在于，进入波区和退出波区，是按最低值的放大倍数而定
'''
import matplotlib.pyplot as pl
import pandas as pd
            



'''
寻找波形
参数area：成交量放大倍数，成交量下降倍数

上升area[0]倍大小进入波区，下降area[1]倍走出波区，area[2]波宽（波形宽度条件没有使用）

1 判断是否进入波区，在此期间不断更新最低点
2 进入波区后，判断是否走出波区
3 判断是否走出波区，使用的是下降到整体波形的80% 或 下降到area[0]倍---该方法的优势是能够较好的找到一个完整的波，缺陷是，如果波没有下降到整体的80%，就不会被识别，可以根据调整下降的比例来改变
'''
def wave_analyze(data, area):    
    # 将数据整体提升，避免有负数和零的情况***存在一个很大的问题，因为找波用的放大倍数因此直接拉升会影响比例关系，但是因为该值无负数，所以没问题
    x = min(data)
    if x <= 0:
        data = data + 1 + abs(x)
    
    wave = []

    left = 0      # 最小点的位置
    middle = 0     # 波形最高值点的位置
    updown = 0
    
    for i in range(len(data)) :
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if data[left] > data[i] :
                left = i
                    
            k_in = area[0] * data[left]
                
            if data[i] > k_in:# 判断是否放大额定倍数，用减法可以允许最小值为负数的情况
                updown = 1 # 进入波区 
                middle = i

        if updown == 1 : # 进入波区 
            # 更新最大点的位置
            if data[middle] < data[i] :
                middle = i

            # 选择走出波区的范围，x1是设置的条件，x2是作为保险条件
            x1 = area[1] * data[i]            # 当前点放大额定倍数
            x2 = min(data[middle]*0.1, k_in)  # 选波高的10% 或 进入波区的高度 

            # 判断是否走出波区
            if data[middle] > x1 or data[i] < x2 :# 针对最高点而言 或  针对整体波高而言
                updown = 0 # 走出波区
                # 此时的波的左值不一定准确，精确找波时，此时可重新更新左值
                
                # 记录波的信息
                wave.append([left, middle, i]) # 记录波的左值，波峰，右值的位置
                # 更新左值，重新找波
                left = i
    
    return wave   


'''
返回成交量的最大倍数
参数
data：成交量
wave：寻找到的波形位置---波的左值，波峰，右值的位置
'''
def deal_max(data, wave):
    dup = [] # 存放成交量的放大倍数
    for l,m,r in wave:
        if data[l] != 0:
            d = data[m]/data[l]
        else:
            d = data[m]
        dup.append(d)
    if len(dup) > 0:
        dm = max(dup)
    else:
        dm = 0
    return dm

if __name__=="__main__":

    # 读取设置参数
    mydf = pd.read_excel('C:\stage11\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
    
    import get_SH
    code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD, code_ma = get_SH.get_stock('600531',setdf)
    '''
    mydf = pd.read_excel('wave.xls')
    code_deal = mydf["wave"].values
    '''
    
    wave = wave_analyze(code_deal, [6, 3, 1]) #6倍大小进入波区，下降到5倍走出波区，1是搜索的区域

    #将原始数据和波峰，波谷画到一张图上
    pl.figure(figsize=(25,8))
    pl.plot(code_deal)

    wave_l =[]
    wave_m =[]
    wave_r =[]
    for i,m,j in wave:
        wave_l.append([i,code_deal[i]])
        wave_m.append([m,code_deal[m]])
        wave_r.append([j,code_deal[j]])

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
对正负情况进行综合分析，没有直接上浮，可以保留原有比例。但是逻辑还不够健全，总觉得还有些没想到，并且进入波区和走出波区并不是对称的
    for i in range(len(data)) :
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if data[left] > data[i] :
                left = i
                    
            if data[left] == 0:
                k1 = area[0] # 如果出现为0的情况，基数默认为1
            elif data[left] < 0: # 如果是负数，上升和下降的判断是反过来的
                if abs(data[left]/area[0]) > 1: # 从负数到零超过额定倍数
                    k1 = data[left]/area[0] * (area[0]-1)
                else: 
                    k1 = (area[0]-1) * data[left] # 从负数到正数
            else:
                k1 = area[0] * data[left]
                
            if data[i] > k1:# 判断是否放大额定倍数，用减法可以允许最小值为负数的情况
                updown = 1 # 进入波区 
                middle = i

        if updown == 1 : # 进入波区 
            # 更新最大点的位置
            if data[middle] < data[i] :
                middle = i

            # 选择走出波区的范围

            if abs(data[middle]/area[1]) > 1:
                k2 = data[middle]/area[1] # 额定下降倍数
            else:
                k2 = data[middle] - area[1]*data[middle]
            
            # 范围，x1是设置的条件，x2是作为保险条件
            x1 = k2 # 当前值的a倍
            x2 = min(data[middle]*0.1, k1)  # 选波高的10% 或 进入波区的高度  或 额定的下降距离

            # 判断是否走出波区
            if data[i] < x1 :#or data[i] < x2 :# 下降了一定的倍数  或  当前值下降到一定高度以下
                updown = 0 # 走出波区
                # 此时的波的左值不一定准确，精确找波时，此时可重新更新左值
                
                # 记录波的信息
                wave.append([left, middle, i]) # 记录波的左值，波峰，右值的位置
                # 更新左值，重新找波
                left = i
    
'''
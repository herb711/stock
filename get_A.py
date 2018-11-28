'''
根据成交量寻找波峰波谷
'''


import matplotlib.pyplot as pl
            
'''
# high最高价, low最低价, area窗口宽度、高度、下降比例 （波形宽度条件没有使用）
1 判断是否进入波区，在此期间不断更新最低点
2 进入波区后，判断是否走出波区
3 判断是否走出波区，使用的是下降到整体波形的80%，
该方法的优势是能够较好的找到一个完整的波
缺陷是，如果波没有下降到整体的80%，就不会被识别，可以根据调整下降的比例来改变
'''
def wave_analyze(vomule, area):
    wave = []

    left = 0
    right = 0
    updown = 0
    for i in range(len(vomule)) :
        if updown == 0: # 没有进入波区 
            # 更新最小点的位置
            if vomule[left] > vomule[i] :
                left = i
            
            if (vomule[i]/vomule[left]) > area[1] :
                updown = 1 # 进入波区 
                right = i
        
        if updown == 1 :
            # 更新最大点的位置
            if vomule[right] < vomule[i] :
                right = i

            h = vomule[right]/vomule[left]
            x = max(h*area[2],area[1])
            # 现在是上升，当下降到80%高度的时候，认为走出波区
            y = vomule[right] / vomule[i]
            if y > x :
                updown = 0 # 走出波区
                wave.append([left, right, i, vomule[right]/vomule[i]]) # 记录波谷，波峰
                left = i
                              
    return wave       


if __name__=="__main__":
    import get_SH
    code_vomule, code_close, code_low, code_high = get_SH.get_stock()
    
    wave = wave_analyze(code_vomule, [1, 6, 0.5])

    #将原始数据和波峰，波谷画到一张图上
    pl.figure()
    pl.plot(code_vomule)

    wave_base =[]
    wave_crest =[]
    for i,j,m,n in wave:
        wave_base.append([i,code_vomule[i]])
        wave_crest.append([j,code_vomule[j]])

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
    
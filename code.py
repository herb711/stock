from optparse import OptionParser 
import os
import pandas as pd
import numpy as np
import get_A
import get_B
import get_C
import get_SH

def search(codes,setdf):
    # 参数读取
    num_v = 5 #成交量放大缩小倍数
    num_dif = num_v + 1 #DIFF中轴浮动范围
    num_dea = num_dif + 1 #DEA中轴浮动范围
    num_macd = num_dea + 1 #MACD中轴浮动范围
    num_kt = num_macd + 1 #K线粘黏时间范围（搜寻长度）
    num_kh = num_kt + 1 #K线粘黏高度范围（搜寻高度）
    
    stock_1 = [] # A C B
    stock_2 = [] # C A
    stock_3 = [] # A B
    
    for code in codes:
        if code == None:
            return stock_1, stock_2, stock_3
    
        code = str(int(code))
                
        code_vomule, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD = get_SH.get_stock(code,setdf)
        
        # 成交量两年内出现放大缩小，至少2次
        A_ok = False
        A = get_A.wave_analyze(code_vomule, [1,setdf[num_v],0.5])
        if len(A) >= 2:
            A_ok = True
            
        # macd diff dea
        B_ok = False
        result = get_B.MDD_analyze(np.array([code_DIFF, code_DEA, code_MACD]), 6, [setdf[num_dif], setdf[num_dea], setdf[num_macd]])  # 6个点半年，后面3个为判定幅度和数据顺序一致
        if len(result) > 0 :
            B_ok = True
                     
        # k                                                                                                                                                                                                                           
        C_ok = get_C.k60_analyze(code_close,code_low,[setdf[num_kt], setdf[num_kh]])
        
        if A_ok and B_ok and C_ok:
            stock_1.append(code)
            
        if A_ok and C_ok:
            stock_2.append(code)
        
        if A_ok and B_ok:
            stock_3.append(code)
    
    return stock_1, stock_2, stock_3

def foo(stocks):
    # 读取设置参数
    mydf = pd.read_csv('set.csv')
    mydf = mydf.where(mydf.notnull(), None) # 去掉空白行
    setdf = mydf["设置参数"].values
    setcode = []
    for eachStock in stocks.split(','):	
        setcode.append(eachStock)
    
    stock_1, stock_2, stock_3 = search(setcode,setdf)
    # 记录
    PATH_SAVE = '筛选结果.csv'
    df = pd.DataFrame({'A C B':stock_1})
    df.to_csv('./ACB'+PATH_SAVE, index = False, mode = 'w')
    df = pd.DataFrame({'C A':stock_2})
    df.to_csv('./CA'+PATH_SAVE, index = False, mode = 'w')
    df = pd.DataFrame({'A B':stock_3})
    df.to_csv('./AB'+PATH_SAVE, index = False, mode = 'w')


if __name__=="__main__":   
	parser = OptionParser() 
	parser.add_option("-s", "--stock",action="store",type="string", dest="stock", default="",help="输入股票代码，例如600620多个股票使用英文逗号相隔") 
	parser.add_option("-d", "--debug",action="store_true", dest="debug",default=False,help="输入股票代码，例如600620多个股票使用英文逗号相隔，使用-h 查看详细")
	parser.add_option("-f", "--file",action="store", type="string",dest="file",default="",help="输入保存股票代码的文件路径")
	parser.add_option("-n", "--new",action="store_true",dest="newFile",default=False,help="创建新的stage1.txt文件")	
	(options, args) = parser.parse_args() 
	if options.newFile==True:
		stage1File=os.getcwd()+'\\Result\\stage1.txt'
		if os.path.exists(stage1File) == True:
			os.remove(stage1File)
		logFile=os.getcwd()+'\\result\\failedStock.txt'
		if os.path.exists(logFile):
			os.remove(logFile)
	if options.debug==True:
		debug=True
	if options.stock:
		foo(options.stock)
	if options.file:
		with open(options.file,"r") as stockFile:
			stockList=stockFile.read()
			foo(stockList)

    
'''
if __name__=="__main__": 
    # 读取设置参数
    mydf = pd.read_csv('set.csv')
    mydf = mydf.where(mydf.notnull(), None) # 去掉空白行
    setdf = mydf["设置参数"].values
    setcode = mydf["股票代码"].values 
    
    stock_1, stock_2, stock_3 = search(setcode,setdf)
    
    # 记录
    PATH_SAVE = '筛选结果.csv'
    df = pd.DataFrame({'A C B':stock_1})
    df.to_csv('./ACB'+PATH_SAVE, index = False, mode = 'w')
    df = pd.DataFrame({'C A':stock_2})
    df.to_csv('./CA'+PATH_SAVE, index = False, mode = 'w')
    df = pd.DataFrame({'A B':stock_3})
    df.to_csv('./AB'+PATH_SAVE, index = False, mode = 'w')
'''    
    
    

'''

for code in setcode :
    #code = "601857"
    code = str(code)

    #使用平安银行的数据
    # open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
    stock = ts.get_hist_data(code, start=date_start, end=date_end)
    stock = stock.sort_index(0)  # 将数据按照日期排序下。
    

    
    #使用成交量寻找波峰波谷：
    volume_wave = pd.Series(stock["volume"].values) # 成交量的日交易数据
    code_wave = wave.wt_analyze(volume_wave, set_v)[4] # '6'为需要取的波峰与波谷之间的倍数
    
    
    ############### 以下为画图显示用 ###############
    wave_crest_x = [] #波峰x
    wave_crest_y = [] #波峰y
    wave_base_x = [] #波谷x
    wave_base_y = [] #波谷y
    for i in code_wave:
        wave_crest_x.append(i[0])
        wave_crest_y.append(i[1])
        wave_base_x.append(i[2])
        wave_base_y.append(i[3])

    #将原始数据和波峰，波谷画到一张图上
    plt.figure()
    plt.plot(volume_wave)
    plt.plot(wave_base_x, wave_base_y, 'go')#蓝色的点
    plt.plot(wave_crest_x, wave_crest_y, 'ro')#红色的点
    plt.grid()
    plt.show()
    
    break    
    
    
'''
    
    
    
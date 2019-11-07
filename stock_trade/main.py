# coding=utf-8   #默认编码格式为utf-8

import os
import time
import pandas as pd
import numpy as np
import cal_deal # 对成交量进行波形分析
import cal_DDM  # DEA DIFF MACD 在中轴线的长度
import cal_MA   # 对k线做出分析
import cal_HL   # 对最高价和最低价做出分析
import get_SH
import GetLongData

# 参数读取
num_v_h = 5 #成交量放大倍数
num_v_d = num_v_h + 1 #成交量缩小倍数
num_dif = num_v_d + 1 #DIFF中轴浮动范围
num_dea = num_dif + 1 #DEA中轴浮动范围
num_macd = num_dea + 1 #MACD中轴浮动范围
num_kt = num_macd + 1 #K线粘黏时间范围（搜寻长度）
num_kh = num_kt + 1 #K线粘黏高度范围（搜寻高度）
num_k60down = num_kh + 1 #判断最低价是否在K60以下（比例）
num_high_in = num_k60down + 1 #波形放大比例，进入波区条件
num_low_out = num_high_in + 1 #在最低点之上再浮动6%


def search(codes,setdf):
    stock_all =[] # 全部筛选结果
    stock_ABC = [] # A B C
    stock_AC = [] # A C
    stock_AB = [] # A B
    stock_B = [] # B
    stock_D = [] # D
    
    for code in codes:
        print('search---',code)
        try:
       
            code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD, code_MA60 = get_SH.get_stock(code,setdf)
    
            # 成交量两年内出现放大缩小，至少2次         
            A_ok = False
            A_wave = cal_deal.wave_analyze(code_deal, [setdf[num_v_h],setdf[num_v_d],1]) # 参数：成交量放大倍数，成交量下降倍数
            if len(A_wave) >= 2: # 有两个波或以上
                A_ok = True
    
    
            # 计算 macd diff dea 在中轴线附近的总长度
            B_ok = False
            B_len = cal_DDM.wave_analyze(np.array([code_DIFF, code_DEA, code_MACD]), [setdf[num_dif], setdf[num_dea], setdf[num_macd]])       
            if B_len > 6 :
                B_ok = True
    
    
            # 判断均线是否有交叉，且最低价在60线以下                                                                                                                                                                                                                  
            C_ok = cal_MA.k60_analyze(code_MA60,code_low,[setdf[num_kt], setdf[num_kh]])
            
            
            # 最高价最低价找波形
            D_ok = False
            D_wave = cal_HL.wave_analyze(code_high, code_low, [setdf[num_high_in],setdf[num_low_out],1]) # 参数：成交量放大倍数，成交量下降倍数
            if len(D_wave) >= 2: # 有两个波或以上
                D_ok = True
                
                
            # 记录
            if A_ok and B_ok and C_ok:
                stock_ABC.append(code)
            if A_ok and B_ok:
                stock_AB.append(code)
            if A_ok and C_ok:
                stock_AC.append(code)
            if B_ok:
                stock_B.append(code)            
            if D_ok:
                stock_D.append(code)
            
            if A_ok or B_len>0 or C_ok or D_ok:
                dm = cal_deal.deal_max(code_deal, A_wave)
                #stock_all.append(["'"+code, dm, B_len]) # csv显示时不会少0
                stock_all.append([code, dm, B_len, C_ok, len(D_wave)])

        except:
            print('error',code)
    
    GetLongData.End()  
    
    # 记录
    PATH_SAVE = r'C:\FTP\Stage11\result'
    # 判断文件夹是否存在
    if not os.path.exists(PATH_SAVE):
        os.mkdir(PATH_SAVE)
        
    txt_write(PATH_SAVE+r'\ABC.txt',stock_ABC)
    txt_write(PATH_SAVE+r'\AB.txt',stock_AB)
    txt_write(PATH_SAVE+r'\AC.txt',stock_AC)
    txt_write(PATH_SAVE+r'\B.txt',stock_B)
    txt_write(PATH_SAVE+r'\D.txt',stock_D)
    
    # 保存所有筛选股票数据
    if len(stock_all)>0:
        stock_all = np.array(stock_all)
        df = {'股票代码':stock_all[:,0],'成交量放大倍数':stock_all[:,1],'稳定于中轴时长':stock_all[:,2],'均线是否交叉':stock_all[:,3],'最高价最低价形成波形个数':stock_all[:,4]}
    else:
        df = []
    df = pd.DataFrame(df)
    df.to_csv(PATH_SAVE+'\All.csv', index = False, mode = 'w', encoding='utf-8-sig')        
    

def full_list(data, max_len):
    '''对数据进行填充，让所有list变成一样的长度'''
    n = max_len - len(data)
    for i in range(n):
        data.append('')
    return data

def txt_write(filename, data):
    """把数据写入文本文件中"""
    file = open(filename, 'w')
    for i in data:
        file.write(str(i) + ',')
    file.close()

def foo(stocks):
    # 读取设置参数
    mydf = pd.read_excel(r'C:\stage11\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
    setcode = []
    for eachStock in stocks.split(','):	
        setcode.append(eachStock)
    
    search(setcode,setdf)
    

if __name__=="__main__":

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 转换成字符串
    print('start...'+t)
    
    # 判断文件是否存在
    file_path = "C:\FTP\Stage11\ok.txt"
    if os.path.exists(file_path): # 如果存在该文件，将其删除
        os.remove(file_path)

    stockList = 0
    with open('C:\stage11\list.txt',"r") as stockFile:
        stockList=stockFile.read()
    if stockList != 0:
        foo(stockList)
    else:
        print('no search stocks')
        
    if not os.path.exists(file_path): # 如果不存在该文件，新建
        file = open(file_path,'w') #创建空文件
        file.close()  
        
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 转换成字符串
    print('end...'+t)     
    
    '''
    parser = OptionParser() 
    parser.add_option("-s", "--stock",action="store",type="string", dest="stock", default="",help="输入股票代码，例如600620多个股票使用英文逗号相隔") 
    parser.add_option("-d", "--debug",action="store_true", dest="debug",default=False,help="输入股票代码，例如600620多个股票使用英文逗号相隔，使用-h 查看详细")
    parser.add_option("-f", "--file",action="store", type="string",dest="file",default="",help="输入保存股票代码的文件路径")
    parser.add_option("-n", "--new",action="store_true",dest="newFile",default=False,help="创建新的stage10.txt文件")	
    (options, args) = parser.parse_args() 
    if options.newFile==True:
        stage1File=os.getcwd()+'\\Result\\stage11.txt'
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
        stockList = 0
        with open(options.file,"r") as stockFile:
            stockList=stockFile.read()
        if stockList != 0:
            foo(stockList)

    '''










'''
# 发生的情况有先后顺序
# 成交量两年内出现放大缩小，至少2次
A = cal_deal.wave_analyze(code_deal, [setdf[num_v_h],setdf[num_v_d],1]) # 6倍进入波区
if len(A) >= 2:
    left = A[-1][2] # 取最后一个波的左值
    data = np.array([code_DIFF[left:], code_DEA[left:], code_MACD[left:]])
    C = cal_MA.k60_analyze(code_close[left:],code_low[left:],[setdf[num_kt], setdf[num_kh]])
    if C == True:
        stock_2.append(code) # A C
        B = get_B.MDD_analyze(data, 6, [setdf[num_dif], setdf[num_dea], setdf[num_macd]])  # 6个点半年，后面3个为判定幅度和数据顺序一致
        if len(B) > 0:
            stock_1.append(code) # A C B
    else:
        B = get_B.MDD_analyze(data, 6, [setdf[num_dif], setdf[num_dea], setdf[num_macd]])  # 6个点半年，后面3个为判定幅度和数据顺序一致
        if len(B) > 0:
            stock_3.append(code) # A B
''' 


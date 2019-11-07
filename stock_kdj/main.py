from optparse import OptionParser 
import os
import pandas as pd
import cal_MA
import cal_KDJ
import get_SH_KDJ
import GetKDJData

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


def search_kdj(codes,setdf):
    stock_A1 = [] # 上限96,下限10,1,判零3,时长大于5
    stock_B1 = [] 
    stock_C1 = []
    stock_D1 = [] 
    stock_E = [] # 上限96,下限28,1,判零999,时长大于1
    stock_A2 = [] # 上限60,下限2,1,判零2,时长大于5
    stock_B2 = []
    stock_C2 = []
    stock_D2 = []

    for code in codes:
        print('search---',code)
        try:
            code_low, code_J, code_ma60, code_ma20 = get_SH_KDJ.get_stock(code,setdf)
            
            print('analysis')
            # 判断是否存在交叉点，并且ma20在ma60之下
            cross = cal_MA.MA_cross(code_ma60, code_ma20)
            if len(cross) < 1 :
                continue # 没有交叉点，不进行筛选
            # 重新选取数据
            n = cross[-1]
            code_low = code_low[n:]
            code_J = code_J[n:]
            code_ma60 = code_ma60[n:]
            
            # 判断第二类的时候，仅使用最后一个波到结束这部分的数据
            i = cal_KDJ.wave_pick(code_J, [setdf[num_kdj_h],setdf[num_kdj_dABC],1,setdf[num_kdj_uABC]])
            data = code_J[i:]
            # A2类
            r, n = cal_KDJ.wave_zero(data, [setdf[num_kdj_h2],setdf[num_kdj_d2ABC],1,setdf[num_kdj_u2A]])
            r = r + i
            k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
            if n > 0 and k60_ok:
                stock_A2.append(code)
            else:
                # B2类
                r, n = cal_KDJ.wave_zero(data, [setdf[num_kdj_h2],setdf[num_kdj_d2ABC],1,setdf[num_kdj_u2B]])
                r = r + i
                k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
                if n > 0 and k60_ok:
                    stock_B2.append(code)
                else:
                    # C2类
                    r, n = cal_KDJ.wave_zero(data, [setdf[num_kdj_h2],setdf[num_kdj_d2ABC],1,setdf[num_kdj_u2C]])
                    r = r + i
                    k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
                    if n > 0 and k60_ok:
                        stock_C2.append(code)
                    else:
                        # D2类
                        r, n = cal_KDJ.wave_zero(data, [setdf[num_kdj_h2],setdf[num_kdj_d2D],1,setdf[num_kdj_u2D]])
                        r = r + i
                        k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
                        if n > 0 and k60_ok:
                            stock_D2.append(code)
                        else:         
    
                            # 判断波形(ABC)1类，首要条件下降到0
                            r, n = cal_KDJ.wave_zero(code_J, [setdf[num_kdj_h],setdf[num_kdj_dABC],1,setdf[num_kdj_uABC]])
                            # 判断最低价是否在k60以下
                            k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
                
                            # 判断零点持续时长
                            if n > 5 and k60_ok:
                                stock_A1.append(code) # A类
                            elif n > 2 and k60_ok:
                                stock_B1.append(code) # B类
                            elif n > 0 and k60_ok:
                                stock_C1.append(code) # C类
                            else:
                                # D1类
                                r, n = cal_KDJ.wave_zero(code_J, [setdf[num_kdj_h],setdf[num_kdj_dD],1,setdf[num_kdj_uD]])
                                k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
                                if n > 0 and k60_ok:
                                    stock_D1.append(code)
                                else:
                                    # E类
                                    r, n = cal_KDJ.wave_zero(code_J, [setdf[num_kdj_h],setdf[num_kdj_dE],1,999])
                                    k60_ok = cal_MA.K60_down(code_ma60, code_low, r, setdf[num_k60down])
                                    if n > 0 and k60_ok:
                                        stock_E.append(code) 
        except:
            print('error',code)
    GetKDJData.End()  
    
    # 记录
    PATH_SAVE = r'C:\FTP\Stage10\result'
    # 判断文件夹是否存在
    if not os.path.exists(PATH_SAVE):
        os.mkdir(PATH_SAVE)
        
    txt_write(PATH_SAVE+r'\A1.txt',stock_A1)
    txt_write(PATH_SAVE+r'\B1.txt',stock_B1)
    txt_write(PATH_SAVE+r'\C1.txt',stock_C1)
    txt_write(PATH_SAVE+r'\D1.txt',stock_D1)

    txt_write(PATH_SAVE+r'\A2.txt',stock_A2)
    txt_write(PATH_SAVE+r'\B2.txt',stock_B2)
    txt_write(PATH_SAVE+r'\C2.txt',stock_C2)
    txt_write(PATH_SAVE+r'\D2.txt',stock_D2)


    txt_write(PATH_SAVE+'\E.txt',stock_E)
    
    # 统一长度
    lens = []
    lens.append(len(stock_A1))
    lens.append(len(stock_B1))
    lens.append(len(stock_C1))
    lens.append(len(stock_D1))
    lens.append(len(stock_A2))
    lens.append(len(stock_B2))
    lens.append(len(stock_C2))
    lens.append(len(stock_D2))
    lens.append(len(stock_E))
    max_len = max(lens)
    stock_A1 = full_list(stock_A1,max_len)
    stock_B1 = full_list(stock_B1,max_len)
    stock_C1 = full_list(stock_C1,max_len)
    stock_D1 = full_list(stock_D1,max_len)
    stock_A2 = full_list(stock_A2,max_len)
    stock_B2 = full_list(stock_B2,max_len)
    stock_C2 = full_list(stock_C2,max_len)
    stock_D2 = full_list(stock_D2,max_len)
    stock_E = full_list(stock_E,max_len)
    
    df = {'A1':stock_A1,'B1':stock_B1,'C1':stock_C1,'D1':stock_D1,'A2':stock_A2,'B2':stock_B2,'C2':stock_C2,'D2':stock_D2,'E':stock_E}
    df = pd.DataFrame(df)
    df.to_csv(PATH_SAVE+'\All.csv', index = False, mode = 'w')

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
    mydf = pd.read_excel('C:\stage10\set.xls')
    mydf = mydf.where(mydf.notnull(), 0) # 去掉空白行
    setdf = mydf["设置参数"].values
    setcode = []
    for eachStock in stocks.split(','):	
        setcode.append(eachStock)
    
    search_kdj(setcode,setdf)
    


if __name__=="__main__":

    print('start...')
    # 判断文件是否存在
    file_path = "C:\FTP\Stage10\ok.txt"
    if os.path.exists(file_path): # 如果存在该文件，将其删除
        os.remove(file_path)

    stockList = 0
    with open('C:\stage10\list.txt',"r") as stockFile:
        stockList=stockFile.read()
    if stockList != 0:
        foo(stockList)
    else:
        print('no search stocks')
        
    if not os.path.exists(file_path): # 如果不存在该文件，新建
        file = open(file_path,'w') #创建空文件
        file.close()    
    print('...end') 
    
    '''
    parser = OptionParser() 
    parser.add_option("-s", "--stock",action="store",type="string", dest="stock", default="",help="输入股票代码，例如600620多个股票使用英文逗号相隔") 
    parser.add_option("-d", "--debug",action="store_true", dest="debug",default=False,help="输入股票代码，例如600620多个股票使用英文逗号相隔，使用-h 查看详细")
    parser.add_option("-f", "--file",action="store", type="string",dest="file",default="",help="输入保存股票代码的文件路径")
    parser.add_option("-n", "--new",action="store_true",dest="newFile",default=False,help="创建新的stage10.txt文件")	
    (options, args) = parser.parse_args() 
    if options.newFile==True:
        stage1File=os.getcwd()+'\\Result\\stage10.txt'
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
        print(os.getcwd())
        print('start...')
        stockList = 0
        with open(options.file,"r") as stockFile:
            stockList=stockFile.read()
        if stockList != 0:
            foo(stockList)
        else:
            print('no search txt')
        print('end...')
   '''
    
    
import pandas as pd
import numpy as np
import GetData

def get_stock(code,setdf):
    
    #stock = pd.read_csv('result.csv')
    stock = GetData.getstock(code)
    
    x = stock.loc[:,['收']].values
    code_close = stock["收"].values # 收盘价
    code_low = stock["低"].values # 最低价
    code_high = stock["高"].values # 最高价、
    code_deal = stock["deal"].values # 成交价   
    code_DIFF = stock["DIFF"].values
    code_DEA = stock["DEA"].values
    code_MACD = stock["MACD"].values 
    
    code_close = np.array(code_close,'float') 
    code_low = np.asarray(code_low,'float') 
    code_high = np.asarray(code_high,'float') 
    code_deal = np.asarray(code_deal,'float') 
    code_DIFF = np.asarray(code_DIFF,'float') 
    code_DEA = np.asarray(code_DEA,'float') 
    code_MACD = np.asarray(code_MACD,'float') 
    
    code_close = code_close.tolist() 
    code_low = code_low.tolist() 
    code_high = code_high.tolist() 
    code_deal = code_deal.tolist() 
    code_DIFF = code_DIFF.tolist() 
    code_DEA = code_DEA.tolist() 
    code_MACD = code_MACD.tolist() 
    
    return code_deal, code_close, code_low, code_high, code_DIFF, code_DEA, code_MACD
    
if __name__=="__main__":
        
    #假设股票数据
    code = "600516"
    setdf = 0
    
    get_stock(code,setdf)
    
    
    
    
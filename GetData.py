from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import pandas as pd


def getMonthData(driver):
    
    stockData={}
    #定位k线
    kLine=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[4]')
    rr=re.compile(r'(.*) 开：(.*) 高：(.*) 低：(.*) 收：(.*) 涨跌：(.*) 涨幅：(.*)')
    a=rr.match(kLine.text).groups()
    b=zip(['年月','开','高','低','收','涨跌','涨幅'],a)
    c=dict(b)

    stockData=c
     #定位成交量
    deal=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[6]')
    #deal.text
    rr=re.compile(r'成交量 量(.*)')
    a=rr.match(deal.text).groups()[0]
    #有万或者亿两个单位
    if '万' in a:
        c=float(a.replace('万',''))*10000
    elif '亿' in a:
        c=float(a.replace('亿',''))*100000000
    else:
        c=a
    stockData['deal']=c

    #定位MACD
    macd=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[7]')
    rr=re.compile(r'MACD: (.*) DIFF: (.*) DEA: (.*)')
    a=rr.match(macd.text).groups()
    b=zip(['MACD','DIFF','DEA'],a)
    c=dict(b)

    stockData=dict(stockData,**c)
    return stockData

def getstock(stock):
    #配置chromeDriver
    options=webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    driver=webdriver.Chrome(chrome_options=options)
    urlPattern=r'http://stockpage.10jqka.com.cn/%s/'
    #获取股票页面
    
    driver.get(urlPattern % stock)
    #切入到iframe
    driver.switch_to.frame(driver.find_element_by_xpath("//*[@id='hqzs']/div/iframe"))
    #点击按月线
    monthButton=driver.find_element_by_xpath("/html/body/ul/li[4]/a")
    monthButton.click()
    time.sleep(2)
    #移动到界面地最左端
    actions = ActionChains(driver)
    panel=driver.find_element_by_xpath("//*[@id='hxc3_cross_testcanvas']")
    #必不可少，因为perform并不会清空历史动作列表
    actions.reset_actions()
    actions.move_to_element_with_offset(panel,0,250)
    actions.perform()
    #添加每次移动1像素的动作，然后不停调用即可
    #这里为何是1呢，因为图像宽618，但是步进是不同的每只股票.
    actions.reset_actions()
    actions.move_by_offset(1, 0)
    monthDataList=[]
    lastMonth=""
    for i in range(618):
    
        actions.perform()
        #获取当前月份的数值
        #time.sleep(0.01)
        data=getMonthData(driver)
        if(data['年月']!=lastMonth):
            data['stock']=stock
            monthDataList.append(data)
            lastMonth=data['年月']
    
    dataFrame=pd.DataFrame(monthDataList)
    return dataFrame

if __name__=="__main__": 
    stock='600516'
    dataFrame = getstock(stock)
    dataFrame.to_csv("result.csv")
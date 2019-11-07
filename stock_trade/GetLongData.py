import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import pandas as pd
from selenium.common.exceptions import WebDriverException

def wheel_element(element, deltaY = 120, offsetX = 0, offsetY = 0):
    error = element._parent.execute_script("""
    var element = arguments[0];
    var deltaY = arguments[1];
    var box = element.getBoundingClientRect();
    var clientX = box.left + (arguments[2] || box.width / 2);
    var clientY = box.top + (arguments[3] || box.height / 2);
    var target = element.ownerDocument.elementFromPoint(clientX, clientY);

    for (var e = target; e; e = e.parentElement) {
      if (e === element) {
        target.dispatchEvent(new MouseEvent('mouseover', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new MouseEvent('mousemove', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new WheelEvent('wheel',     {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY, deltaY: deltaY}));
        return;
      }
    }    
    return "Element is not interactable";
    """, element, deltaY, offsetX, offsetY)
    if error:
        raise WebDriverException(error)

def getDayOrWeekData(driver):
    
    stockData={}
    #定位k线
    kLine=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[4]')
    #print(kLine.text)
    rr=re.compile(r'(.*) 开：(.*) 高：(.*) 低：(.*) 收：(.*) 涨跌：(.*) 涨幅：(.*)')
    a=rr.match(kLine.text).groups()
    b=zip(['年月日','开','高','低','收','涨跌','涨幅'],a)
    c=dict(b)

    stockData=c
    #定位MA
    maLine=driver.find_element_by_css_selector('#testcanvas > div.hxc3-hxc3KlinePricePane-hover-ma')
    #print(maLine.text)
    rr=re.compile(r'MA5: (.*) MA10: (.*) MA30: (.*)')
    try:
        a=rr.match(maLine.text).groups()
    except:
        a=[0,0,0]
    b=zip(['MA5','MA10','MA30'],a)
    c=dict(b)
    stockData=dict(stockData,**c)
     #定位成交量
    deal=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[6]')
    #deal.text
    #print(deal.text)
    rr=re.compile(r'成交量 量(.*)')
    a=rr.match(deal.text).groups()[0]
    #有万或者亿两个单位
    if '万' in a:
        c=float(a.replace('万',''))*10000
    elif '亿' in a:
        c=float(a.replace('亿',''))*100000000
    else:
        c=a
    #b=zip(['成交量'],c)
    c=dict({"成交量":c})
    stockData=dict(stockData,**c)

    #定位MACD
    macd=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[7]')
    #print(macd.text)
    rr=re.compile(r'MACD: (.*) DIFF: (.*) DEA: (.*)')
    a=rr.match(macd.text).groups()
    b=zip(['MACD','DIFF','DEA'],a)
    c=dict(b)

    stockData=dict(stockData,**c)
    return stockData

#配置chromeDriver
options=webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
driver=webdriver.Chrome(chrome_options=options)
urlPattern=r'http://stockpage.10jqka.com.cn/%s/'
def Start(stock):
    #获取股票页面
    #stock='600077'
    driver.get(urlPattern % stock)
    #切入到iframe
    driver.switch_to.frame(driver.find_element_by_xpath("//*[@id='hqzs']/div/iframe"))
    #点击按日线
    dayButton=driver.find_element_by_xpath("/html/body/ul/li[2]/a")
    dayButton.send_keys('\n')#click超出显示范围则无法点击，click完全模拟鼠标操作。

    #点击MACD
    MACDButton=driver.find_element_by_xpath('//*[@id="testcanvas"]/div[2]/ul/li[1]/a')
    MACDButton.send_keys('\n')
    time.sleep(2)
    #移动到界面地最左端
    actions = ActionChains(driver)
    panel=driver.find_element_by_xpath("//*[@id='hxc3_cross_testcanvas']")
    #进行缩放
    
    for x in range(10):
        wheel_element(panel,120)
        
    #time.sleep(50)
    #必不可少，因为perform并不会清空历史动作列表

    actions.reset_actions()
    actions.move_to_element_with_offset(panel,0,250)
    actions.perform()
    #添加每次移动1像素的动作，然后不停调用即可
    #这里为何是1呢，因为图像宽618，但是步进是不同的每只股票.
    actions.reset_actions()
    actions.move_by_offset(1, 0)
    dayDataList=[]
    lastDay=""
    for i in range(618):

        actions.perform()
        #获取当前日的数值
        #time.sleep(0.01)
        data=getDayOrWeekData(driver)
        #去重
        if(data['年月日']!=lastDay):
            data['stock']=stock
            dayDataList.append(data)
            lastDay=data['年月日']

    dataFrame_day=pd.DataFrame(dayDataList)
    #dataFrame.to_csv("%s_dayresult.csv" % stock)

    ###########周数据
    #点击按周线
    #切入到iframe
    #driver.refresh()
    #driver.switch_to.frame(driver.find_element_by_xpath("//*[@id='hqzs']/div/iframe"))
    dayButton=driver.find_element_by_xpath("/html/body/ul/li[3]/a")
    dayButton.send_keys('\n')
    #点击KDJ
    MACDButton=driver.find_element_by_xpath("//*[@id='testcanvas']/div[2]/ul/li[1]/a")
    MACDButton.send_keys('\n')
    #进行缩放
    
    
    time.sleep(2)
    #移动到界面地最左端
    actions = ActionChains(driver)
    panel=driver.find_element_by_xpath("//*[@id='hxc3_cross_testcanvas']")
    for x in range(5):
        wheel_element(panel,120)

    #必不可少，因为perform并不会清空历史动作列表
    actions.reset_actions()
    actions.move_to_element_with_offset(panel,0,250)
    actions.perform()
    #添加每次移动1像素的动作，然后不停调用即可
    #这里为何是1呢，因为图像宽618，但是步进是不同的每只股票.
    actions.reset_actions()
    actions.move_by_offset(1, 0)
    weekDataList=[]
    lastWeek=""

    for i in range(618):

        actions.perform()
        #获取当前月份的数值
        #time.sleep(0.01)
        data=getDayOrWeekData(driver)
        if(data['年月日']!=lastWeek):
            data['stock']=stock
            weekDataList.append(data)
            lastWeek=data['年月日']

    dataFrame_week=pd.DataFrame(weekDataList)
    #dataFrame.to_csv("%s_weekresult.csv" % stock)
    
    #########获取月数据
    
    #切入到iframe
    #driver.refresh()
    #driver.switch_to.frame(driver.find_element_by_xpath("//*[@id='hqzs']/div/iframe"))
    dayButton=driver.find_element_by_xpath("/html/body/ul/li[4]/a")
    dayButton.send_keys('\n')
    #点击MACD
    MACDButton=driver.find_element_by_xpath("//*[@id='testcanvas']/div[2]/ul/li[1]/a")
    MACDButton.send_keys('\n')
    #进行缩放
    
    
    time.sleep(2)
    #移动到界面地最左端
    actions = ActionChains(driver)
    panel=driver.find_element_by_xpath("//*[@id='hxc3_cross_testcanvas']")
    for x in range(5):
        wheel_element(panel,120)

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
        data=getDayOrWeekData(driver)
        if(data['年月日']!=lastMonth):
            data['stock']=stock
            monthDataList.append(data)
            lastMonth=data['年月日']

    dataFrame_month=pd.DataFrame(monthDataList)
    #dataFrame.to_csv("%s_monthresult.csv" % stock)
    
    return dataFrame_day,dataFrame_week,dataFrame_month
    
def End():
    driver.quit() # 游览器关闭

if __name__=="__main__": 
    stock='600516'
    dataFrame_day,dataFrame_week,dataFrame_month = Start(stock)
    dataFrame_day.to_csv("result.csv")
    End()


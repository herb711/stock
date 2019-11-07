import pandas as pd


def getstock(code):

    dataFrame_day = pd.read_csv('./test/' + code + '_dayresult.csv')
    dataFrame_week = pd.read_csv('./test/' + code + '_weekresult.csv')

    return dataFrame_day, dataFrame_week
    
if __name__=="__main__":
      getstock('600077')
    
    
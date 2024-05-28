import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date


#setup
print ('Please enter what you would like to name the file with all the actions. We recommend \"Month_Year_actions.txt\"')
actionsFile = input()
print('Please enter what you would like the outputted csv file to be named')
csvFile = input()
print('Add file path to your csv containing portfolio status.')
historyCsv = input()
actions = open(actionsFile, "a")
actions.write(str(date.today()) + "\n")

counter = 0
tickerNames = 'JNJ KO JPM MCD MMM MRK MSFT NKE PG TRV UNH CRM VZ V WBA WMT DIS DOW AXP AMGN AAPL BA CAT CSCO CVX GS HD HON IBM INTC'

print("These are the following stocks we will examine:" + tickerNames)
ticker = tickerNames.split()
tickerInfo = [yf.Ticker(ticker[0]).info.items()]

#find all EPS values and move them into an array
#move all EPS value tickers into an ans array to index lookup later
#this is just for the first ticker
for key, value in tickerInfo[0]:
        if (key == 'trailingEps'):
            eps = [value]
            epsDict = {ticker[0] : eps[0]}
            break
#iterate through the array to retrieve EPS and ticker name for each element
while (counter<len(ticker)-1):
    counter+=1
    tickerInfo.append(yf.Ticker(ticker[counter]).info.items())
    for key, value in tickerInfo[counter]:
        if (key == 'trailingEps'):  
            eps.append(value)
            epsDict.update({ticker[counter] : value})
            break
eps.sort(reverse=True)

tempKey = ''
tempVal = 0
for key, value in epsDict.items(): 
     if (value == eps[0]):
          tempKey = key
          tempVal = value
          break 
     
sortedEpsDict = {tempKey : tempVal}
counter = 1 
while (counter < len(eps)):
     for key,value in epsDict.items(): 
         if (value == eps[counter]):
          sortedEpsDict.update({key : value})
          break
     counter+=1

topFiveDict = {}

counter = 0

for key, value in sortedEpsDict.items():
    if (counter<5):
        topFiveDict.update({key:value})
        counter+=1
    else: 
        break



'''

by this point in the code we have the following variables 
tickerNames -> a string with the collection of the 30 stocks in the Dow Jones Inducstiral average
ticker-> an array of strings with each ticker separated 
tickerInfo-> an array of dictionaries with each ticker's dictionary in order of the tickers in the ticker array 
eps -> an array of eps values in order of the tickers in the ticker array, sorted in descending order
epsDict-> a dictionary formatted {ticker : eps} 
sortedEpsDict-> the epsDict rearranced to rank stocks with highest to lowest eps value, formatted {ticker :eps}
topFiveDict-> a smaller dictionary that only has the ticker and eps values of the top 5 stocks ranked by eps

AT THIS POINT IN THE CODE, ALL DOW J EPS RANKINGS HAVE BEEN COMPLETE. NOW THE 
PROGRAM WILL READ THE DATA FROM THE CSV FILE AND SUGGEST PORTFOLIO CHANGES 
'''


df = pd.read_csv(historyCsv)
pd.set_option('display.max_columns', None)


ser = df.get(["Ticker"]) 
ser1= df.get(["EPS"])
ser2= df.get(["Price"])
ser3= df.get(["Qty"])
ser4= df.get(["Holdings"])


count = 1
tempTickerArray = ser.to_numpy()
tempEPSArray = ser1.to_numpy()
tempPriceArray = ser2.to_numpy()
tempQuantityArray = ser3.to_numpy()
tempHoldingsArray = ser4.to_numpy()
tempTickerArrayStrings= [tempTickerArray[0][0]]
tempEPSArrayOut = [tempEPSArray[0][0]]
tempPriceArrayOut = [tempPriceArray[0][0]]
tempQuantityArrayOut = [tempQuantityArray[0][0]]
tempHoldingsArrayOut = [tempHoldingsArray[0][0]]

#all of the arrays and variables above are for moving the data from the data frame to dictionaries

#move data from dataframe to arrays temporarily
while(count < 5):
    tempTickerArrayStrings.append(tempTickerArray[count][0])
    tempEPSArrayOut.append(tempEPSArray[count][0])
    tempPriceArrayOut.append(tempPriceArray[count][0])
    tempQuantityArrayOut.append(tempQuantityArray[count][0])
    tempHoldingsArrayOut.append(tempHoldingsArray[count][0])
    count+=1


#move data from arrays to dictionaries 
count = 1
pastEpsDict = {tempTickerArrayStrings[0] : tempEPSArrayOut[0]}
priceDict = {tempTickerArrayStrings[0] : tempPriceArrayOut[0]}
quantityDict = {tempTickerArrayStrings[0] : tempQuantityArrayOut[0]}
holdingsDict = {tempTickerArrayStrings[0] : tempHoldingsArrayOut[0]}


while (count < len(tempEPSArrayOut)):
    pastEpsDict.update({tempTickerArrayStrings[count] : tempEPSArrayOut[count]})
    priceDict.update({tempTickerArrayStrings[count] : tempPriceArrayOut[count]})
    quantityDict.update({tempTickerArrayStrings[count] : tempQuantityArrayOut[count]})
    holdingsDict.update({tempTickerArrayStrings[count] : tempHoldingsArrayOut[count]})
    count+=1
    

'''
by this point in the code we have the following variables: 
pastEpsDict -> a dictionary with all stocks previously invested in and their eps, formatted {ticker : EPS}
priceDict -> a dictionary with all stocks previously invested in and their stockprice at investment, formatted {ticker : EPS}
quantityDict -> a dictionary with all stocks previously invested in and the quantity invested , formatted {ticker : quantity}
holdingsDict -> a dictionary with all stocks previously invested in and the total amount of $ invested in each, formatted {ticker : holdings}
'''


'''
print (df)
print ()
print ('the top 5 stocks with highest eps are: ', topFiveDict)
print()
print('past EPS dict', pastEpsDict)
print('price dictionary' , priceDict)
print('quantity dict' , quantityDict)
print('holdings dict', holdingsDict)

'''


removeArray = []
for element in tempTickerArrayStrings:
    if (not(element in topFiveDict.keys())): 
        removeArray.append(element)

cash = 0


for name in quantityDict:
    for key, value in yf.Ticker(name).info.items():
        if (key == "currentPrice"): 
            cash += value * quantityDict.get(name)
            if (name in removeArray):
                out = "We must sell all "+ str(quantityDict.get(name))+ " shares of "+ name + " at "+ str(value)+ ", leaving us with "+ str(value*quantityDict.get(name))+ "\n"
                actions.write(out)
          


cashAllowance = round(cash / 5)
finalQtyDict = {}
finalPriceDict={}
finalHoldingsDict={}

for name in topFiveDict: 
    for key, value in yf.Ticker(name).info.items():
         if (key == "currentPrice"): 
            finalQtyDict.update({name : round(cashAllowance/value)})
            finalPriceDict.update({name : value})
            finalHoldingsDict.update({name : value * round(cashAllowance/value)})
out = "current portfolio value is: " + str(cash) + "\n"
actions.write(out)

for key in finalQtyDict:
   
    if (key in quantityDict):
        temp = round(finalQtyDict.get(key) - quantityDict.get(key),0)
        if (temp <0):
            out = "sell "+ str(-1*temp)+ " shares of "+ str(key)+ " at "+ str(finalPriceDict.get(key))+ "\n"
            actions.write(out)
        else: 
            out = "buy " + str(temp) + " shares of "+ str(key)+ " at "+ str(finalPriceDict.get(key)) + "\n"
            actions.write(out)
    else:
        out = "buy "+ str(round(finalQtyDict.get(key),0))+ " shares of "+ str(key)+ " at "+ str(finalPriceDict.get(key)) + "\n"
        actions.write(out)
        
actions.write("Ultimately, we will be investing in these top 5 stocks per their EPS: " + "\n" + str(topFiveDict))
actions.close()


finalTickers = [] 
finalQuantities = []
finalPrices = []
finalHoldings = []
finalEPS=[] 

for element in topFiveDict:
    finalTickers.append(element)
    finalEPS.append(topFiveDict.get(element))
    finalQuantities.append(finalQtyDict.get(element))
    finalPrices.append(finalPriceDict.get(element))
    finalHoldings.append(finalHoldingsDict.get(element))

data = {'Ticker': finalTickers , 'EPS': finalEPS, 'Price': finalPrices, 'Qty' : finalQuantities, 'Holdings' : finalHoldings }
dtf = pd.DataFrame(data)

dtf.to_csv(csvFile, index=False)

print("Thank you for using our services! See you next quarter")


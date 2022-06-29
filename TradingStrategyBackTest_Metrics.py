#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:08:52 2022

@author: Robert_Hennings
"""

# This short script should cover six important steps for the purpose of setting up a trading strategy and specifically backtesting it 

# The single steps:
    # 1) Getting stock data 
    # 2) Cleaning the data 
    # 3) Basic plotting of the data 
    # 4) Backtesting the strategy 
    # 5) Calculate the Sharpe Ratio 
    # 6) Calculate the maximum Drawdown 
    
    
########################### 1) Getting the stock data

#The stock Data will be extracted using Yahoo Finance API 
import yfinance as yf #Import the library
aapl = yf.download("AAPL", start="2017-01-01", end="2019-01-01") #loading Stock data for Apple as an example
print(aapl.head()) #show the first few rows of the DataFrame

#some days are skipped becuase they werent trading days
#the difference between the Close column and the Aj Close is that the adjusted column takes into account stock splits and dividends

#it is even possible to get intraday data with parameters from the yf.download method
aapl_intra = yf.download("AAPL", interval="5M", start="2022-05-01", end="2022-06-29") #downloading data in 5 Minute intervals 
print(aapl_intra.head())

#intrasay data is only available for the last 60 days
#Getting a specific column of the data can be achieved via various methods
print(aapl.Open)  #first method

print(aapl.loc[:,"Open"]) #second method 

#get a single data point
aapl.loc["2017-01-03", "Open"]

#Displaying a range of data
print(aapl.loc["2018-12-01":"2018-12-28", "Open"]) 

#Display multiple columns for a period
print(aapl.loc["2018", "Close":"Adj Close"])

#print the index
print(aapl.index)
print(aapl.index.name)

#get a specific date
print(aapl.index[4])

#simultaneously load stock data of more stocks
stock_data = yf.download(["AAPL", "MSFT"], start="2017-01-01", end ="2019-01-01")
print(stock_data.head())

#if we now want to acces the Adj Close column from Apple we acces it like that
print(stock_data.loc[:,("Adj Close", "AAPL")])  #put both headers now instead of only one previously

#get a specific data point just like before but with providing two headers
print(stock_data.loc["2018-12-12", ("Adj Close", "MSFT")])

#Display a range of of values
print(stock_data.loc["2018-12-01":"2018-12-12", ("Adj Close", "AAPL")])

#if the headers allow it is also possible to do it like that
print(stock_data.Open.AAPL) 

#or just simply use .iloc
print(stock_data.iloc[0,1:3])
print(stock_data.iloc[0:10,1:3])


########################### 2) Cleaning the Data

#See how many values are a NaN
print(aapl.isna().sum()) 

#if there would be NaN values we would have to fill them or drop them accordingly
#main methods are forwardfill and backfill, holding a certain value constant

#Forwardfill: use the value in tyhe previous row (row i-1) to fill the next one (row i)
#Backfill: uses row i+1 to fill row i

#Example Forwardfill
aapl_withNa = aapl.iloc[:10,:]
#fill in some random NaN values
import numpy as np 
for i,j in zip(np.random.randint(low=0,high=7,size=8),np.random.randint(low=0,high=7,size=8)):
    aapl_withNa.iloc[i,j] = np.nan
#Look at the data
print(aapl_withNa)
print(aapl.isna().sum())
#Now fill the data with the two methods

print(aapl_withNa.ffill())
print(aapl_withNa.bfill())

########################### 3) Plotting the price data
import matplotlib.pyplot as plt 

#Plot the Adj Close of Apple
plt.plot(aapl.loc[:,"Adj Close"])
plt.xticks(rotation=45)
plt.show()


#Plotting the Adj Close of Apple and Microsoft together
plt.plot(stock_data.loc[:,("Adj Close")])
plt.xticks(rotation=45)
plt.show()


#Add some more elements to the graph
#Change the size of the figure
plt.figure(figsize=(15,8))
#Add tilte and axis names
plt.title("AAPL and MSFT over time", fontsize=20)
plt.xlabel("Date", fontsize=14)
plt.ylabel("Adjusted Close", fontsize=14)
#Plotting the two lines
plt.plot(stock_data.loc[:,("Adj Close", "AAPL")], "-b", label="AAPLE")
plt.plot(stock_data.loc[:,("Adj Close", "MSFT")], "-y", label="MSFT")
plt.legend()
plt.show()



########################### 4) Creating the Backtest

#Idea: Test how a stretgy would have performd on past data

#Strategy: Buy on the first day using the entire capital of 100000$, sell then everything 21 days later, 7 trading days later we buy as much as we can again 
#and keep it for 21 days and so on

import math  
days = 0 #the number of days of the strategy
capital = 100000 #starting capital
shares_bought = 0 #to keep track of the last action (if it was a buy or sell) and how many
portfolio_value = np.array([]) 

#Loop through each trading day in th test
for adj_close in aapl.loc[:,"Adj Close"]:
    #Buy condition: buy every 7 days if we have not bought yet
    if days % 7 == 0 and shares_bought == 0:
        #Check how many shares w can buy
        buy_price = adj_close #Buying at the current price
        max_shares = capital / buy_price #Max shares we can buy
        shares_bought = math.floor(max_shares) #not consider fractional shares so rounding here
        
        #Update the capital
        capital = (max_shares - shares_bought)*adj_close 
        
        print(f"Bought {shares_bought} shares at a price of {buy_price} per share.")
        
    #Sell condition
    elif days % 28 == 0 and shares_bought >0:
        
        #Sell the number of shares bought
        sell_price = adj_close
        shares_sold = shares_bought #buying and selling it all
        value = sell_price * shares_sold 
        
        #Update the capital
        capital += value 
        shares_bought = 0
        
        print(f"sold {shares_sold} at a price of {sell_price} per share.")
        print(f"The value of the portfolio is now {round(capital)}$.\n")
    
    #Track the portfolio value at each time step 
    #Define Portfolio value = Capital = Value of stocks held
    portfolio = capital + (shares_bought * adj_close)
    portfolio_value = np.append(portfolio_value, portfolio)
    
    #Incerement the number of days by one
    days +=1
    
    
#Look at the portfolio value for the first 5 trading days
print(portfolio_value[0:5]) 

#Calculate the return from the first to the last trading day
perc_return = ((portfolio_value[-1] / portfolio_value[0]) -1) * 100  

print(f"We made a return of {round(perc_return,2)}% by trading AAPL across {len(aapl.index)} trading days.")

#The Portfolio_value in a graph

plt.figure(figsize=(15,8))
plt.title("Portfolio Value", fontsize=20)
plt.xlabel("Date", fontsize=14)
plt.ylabel("Value = Capital = Value of Open Positions", fontsize=14)
plt.plot(stock_data.index, portfolio_value)
plt.show()




#Lets compare the strategy with a buy and Hold setting
starting_capital = 100000 
buy_price = aapl.loc[:,"Adj Close"][0] #Price of the first day

shares_bought = math.floor(starting_capital / buy_price)

#Plot the Buy and Hold Profits
plt.figure(figsize=(15,8))
plt.title("AAPL and MSFT Adj Closing Price over Time", fontsize = 20)
plt.xlabel("Date", fontsize = 14)
plt.ylabel("Portfolio Value", fontsize = 14)

plt.plot(stock_data.index, portfolio_value, label = "Strategy")
plt.plot(stock_data.index, shares_bought * aapl.loc[:,"Adj Close"].values, label = "Buy and Hold")
plt.legend()
plt.show()



########################### 5) Calculate the Sharpe Ratio
#Computing the risk adjusted returns
#Sharpe Ratio = (Mean Portfolio Return - Risk free rate) / (Standard Deviation of Portfolio returns)
#Assume Risk free rate is 0%
#Annualize the Sharpe Ratio by: Annualized Sharpe Ratio = Square Root of 252 * Sharpe Ratio

pct_change = pd.Series(portfolio_value).pct_change(1) #Transofrm the numpy array to a pd.Series to compute the % return

print(pct_change)

#Calculate the mean return 
daily_mean_return = pct_change.mean()
print(daily_mean_return) 

#Now compute the volatility as standard deviation of the returns
std = pct_change.std()
print(std) 


#Calculate the Sharpe Ratio
sharpe_ratio = daily_mean_return / std 
print(round(sharpe_ratio,3))

#Annualize the Sharpe Ratio
annualized_sharpe = (252 ** 0.5) * sharpe_ratio 
print(round(annualized_sharpe,3))

"""
Usually, any Sharpe ratio greater than 1.0 is considered acceptable to good by investors.
A ratio higher than 2.0 is rated as very good.
A ratio of 3.0 or higher is considered excellent.
A ratio under 1.0 is considered sub-optimal.
"""



########################### 6) Calculate the Maximum Drawdown
"""
The maximum drawdown (MDD) is the max % loss that you had on your portfolio between a peak and a subsequent trough. 
As an exercise, try to find where the maximum drawdown was on our plot in Part 4.
"""
df_returns = pd.DataFrame(pd.Series(portfolio_value).pct_change(1)) #Create a df with the daily percentage changes
cum_returns = (1+df_returns).cumprod() #Cumulative return (done by multipling sucessive returns eg. 1.01 * 1.03 = a cumulative return of 1.0403)

drawdown = 1 - cum_returns.div(cum_returns.cummax()) #Invert the plot


plt.figure(figsize = (15,8))
plt.title("Cumulaive return of our strategy on Apple", fontsize = 20)
plt.xlabel("Date", fontsize = 14)
plt.ylabel("Cumulatve % Return", fontsize = 14)
plt.plot(stock_data.index, cum_returns.values)
plt.show()




# Change the size of our plot
plt.figure(figsize=(15, 8))

# Add title and axis names
plt.title('Drawdown over time',fontsize=18)
plt.xlabel('Date',fontsize=14)
plt.ylabel('Drawdown',fontsize=14)

# Plotting the two seperate lines with their own labels
plt.plot(stock_data.index, drawdown.values)


#Calculate the MDD

MDD = drawdown.max()*100

print(f'The maximum drawdown (MDD) is approximately {int(round(MDD))}%.')
















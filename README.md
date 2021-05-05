# Stock Market Timing Algorithm Analysis

Goal: Develop a program that illustrates the performance of market timing algorithms. Market timing involves strategically pulling in and out of the stock market at certain times in order to avoid drops in the market. 

Results: Using an algorithm that exits the market when stock value has been decreasing for 5 months consecutively, we conclude that it was able to be beneficial in 81% of 5-year intervals from 1995-2021. We applied the algorithm to real data from SPDR S&P 500 Trust over the last 25 years. With an investment of $1000.00 on 1/31/1995, the algorithm will lead you to $13,323.41 on 1/29/2021, versus $12,642.66 without.

Files:

getStockData.py : main file which collects, cleans, and evaluates stock data using Tiingo API and builds tables/visualizations to analyze performance of the algorithm (using variables such as Monthly Returns, Drawdowns, CAGR)
New25.csv, unadjustedSummary.csv, adjustedSummary.csv are these tables

interval(1-20)_rawdata.csv : show stock data and algorithm performance over 5 year intervals, which I used to confirm the proportion of 5-year intervals that the algorithm helped

Final_table.csv : Summarizes data over last 25 years in 5 year intervals, showing final results

Illustration.png : graphically illustrates the different performances adjacently

Anywhere in the project, “Unadjusted” refers to the regular market and “Adjusted” refers to using the timing algorithm


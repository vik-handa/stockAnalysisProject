from datetime import datetime
import requests, json
import pandas as pd
import matplotlib.pyplot as plt

#retrieve Tiingo data with a dataframe
token = '63753ff0e6fc15c8593da0ccaca6238f7b6abe6e'
Ticker = 'SPY'
startDate = '1995-01-02'
headers = {
        'Content-Type': 'application/json',
        'Authorization' : 'Token ' + token
        }

requestResponse = requests.get('https://api.tiingo.com/tiingo/daily/'+ Ticker +'/prices?startDate=1995-01-02&endDate=2021-01-01&resampleFreq=monthly', headers=headers)
data = requestResponse.json()
df = pd.DataFrame(data)

#Takes only the date and AdjClose Columns from the downloaded data
#and truncates each date to exclude the time
#takes '2020-09-30T00:00:00.000Z' to '2020-09-30'
df = df[['date', 'adjClose']]
rowCount = len(df.index)
for i in range(0, rowCount):
        val = df.at[i, 'date']
        df.at[i, 'date'] = val[:10]

#initialize columns as long type and name them
m1_change = df['adjClose']
m1_change = m1_change.pct_change()

m5_change = df['adjClose']
m5_change = m5_change.pct_change(periods=5)

equity_unadjusted = [0.00]
equity_unadjusted = pd.Series(equity_unadjusted)

market = [0.00]
market = pd.Series(market)
truth_val = (m1_change > 0) | (m5_change > 0)
market = truth_val
market[0] = True
market[1] = True
market[2] = True

equity_adjusted = [0.00]
equity_adjusted = pd.Series(equity_adjusted)

CAGR_adjusted = [0.00]
CAGR_adjusted = pd.Series(CAGR_adjusted)

CAGR_unadjusted = [0.00]
CAGR_unadjusted = pd.Series(CAGR_unadjusted)

max_unadjusted = [0.00]
max_unadjusted = pd.Series(max_unadjusted)

max_adjusted = [0.00]
max_adjusted = pd.Series(max_adjusted)

DD_unadjusted = [0.00]
DD_unadjusted = pd.Series(DD_unadjusted)

DD_unadjusted_perc = [0.00]
DD_unadjusted_perc = pd.Series(DD_unadjusted_perc)

DD_adjusted = [0.00]
DD_adjusted = pd.Series(DD_adjusted)

DD_adjusted_perc = [0.00]
DD_adjusted_perc = pd.Series(DD_adjusted_perc)

ratio = [0.00]
ratio = pd.Series(ratio)

#Initialize dataframe columns with those series
df['1 Month Change'] = m1_change
df['5 Month Change'] = m5_change
df['Unadjusted Equity'] = equity_unadjusted
df['In Market?'] = market
df['Adjusted Equity'] = equity_adjusted
df['Adjusted CAGR'] = CAGR_adjusted
df['Unadjusted CAGR'] = CAGR_unadjusted
df['Max Unadjusted'] = max_unadjusted
df['Max Adjusted'] = max_adjusted
df['DD Unadjusted'] = DD_unadjusted
df['DD Unadjusted Percentage'] = DD_unadjusted_perc
df['DD Adjusted'] = DD_adjusted
df['DD Unadjusted Percentage'] = DD_adjusted_perc
df['Sharpe Ratio'] = ratio

#fix Market Participation row error
df['In Market?'] = df['In Market?'].shift(1)

#initial values for column calculations
priceA = 1000
priceB = 1000
df.at[0, 'Unadjusted Equity'] = 1000
df.at[0, 'Adjusted Equity'] = 1000
maxUnadj = 0
maxAdj = 0
ratio = 0

for i in range(1, rowCount):
    #Calculate Unadjusted Equity
    df.at[i, 'Unadjusted Equity'] = (priceA * (df.iloc[i,2] + 1))
    priceA = df.at[i, 'Unadjusted Equity']

    #Calculate maximum for unadjusted equity
    if priceA > maxUnadj:
        maxUnadj = priceA
    df.at[i, 'Max Unadjusted'] = round(maxUnadj, 4)

    #Depending on 'In Market?' value, adjust equity with stock market changes
    if df.at[i, 'In Market?']:
        df.at[i, 'Adjusted Equity'] = (priceB * (df.iloc[i, 2] + 1))
        priceB = df.at[i, 'Adjusted Equity']
    else:
        df.at[i, 'Adjusted Equity'] = priceB
        priceB = df.at[i, 'Adjusted Equity']

    # Calculate maximum for adjusted equity
    if priceB > maxAdj:
        maxAdj = priceB
    df.at[i, 'Max Adjusted'] = round(maxAdj, 4)

    #Calculate CAGRs
    years = df.at[i, 'date']
    years = int(years[0:4]) - 1995
    if years > 0:
        df.at[i, 'Adjusted CAGR'] = round(((df.at[i, 'Adjusted Equity'] / 1000) ** (1 / years) - 1), 4)
        df.at[i, 'Unadjusted CAGR'] = round(((df.at[i, 'Unadjusted Equity'] / 1000) ** (1 / years) - 1), 4)

#Calculate dropdowns and their percentages
df['DD Unadjusted'] = df['Max Unadjusted'] - df['Unadjusted Equity']
df['DD Unadjusted Percentage'] = df['DD Unadjusted'] / df['Max Unadjusted']
df['DD Adjusted'] = df['Max Adjusted'] - df['Adjusted Equity']
df['DD Adjusted Percentage'] = df['DD Adjusted'] / df['Max Adjusted']

#temporary fix to help readibility
df['Adjusted Equity'] = round(df['Adjusted Equity'], 4)
df['Unadjusted Equity'] = round(df['Unadjusted Equity'], 4)
df['1 Month Change'] = round(df['1 Month Change'], 4)
df['5 Month Change'] = round(df['5 Month Change'], 4)
df['adjClose'] = round(df['adjClose'], 4)

#create dataframe to compare following variables
analysis1 = pd.DataFrame(columns = ['Adjusted CAGR', 'Adj Std Dev', 'Adj Max DD', 'Adj SSR', 'Unadjusted CAGR', 'Unadj Std Dev', 'Unadj Max DD', 'Unadj SSR'])
rowCount2 = len(analysis1.index)

#copies CAGR values from main dataframe
analysis1["Adjusted CAGR"] = df['Adjusted CAGR']
analysis1["Unadjusted CAGR"] = df['Unadjusted CAGR']

#variables and loop is to update the standard deviation
#and the max drawdowns overtime
std_calculator1 = pd.Series(dtype = 'float64')
std_calculator2 = pd.Series(dtype = 'float64')
maxDD1 = 0
maxDD2 = 0
for i in range(12, rowCount):
    std_calculator1.at[i] = analysis1.iloc[i,0]
    analysis1.at[i, 'Adj Std Dev'] = std_calculator1.std()

    std_calculator2.at[i] = analysis1.iloc[i, 4]
    analysis1.at[i, 'Unadj Std Dev'] = std_calculator2.std()

    if df.at[i, 'DD Adjusted'] > maxDD1:
        maxDD1 = df.at[i, 'DD Adjusted']
    analysis1.at[i, 'Adj Max DD'] = maxDD1

    if df.at[i, 'DD Unadjusted'] > maxDD2:
        maxDD2 = df.at[i, 'DD Unadjusted']
    analysis1.at[i, 'Unadj Max DD'] = maxDD2

    analysis1.at[i, 'Adj SSR'] = analysis1.at[i, 'Adjusted CAGR'] / analysis1.at[i, 'Adj Std Dev']
    analysis1.at[i, 'Unadj SSR'] = analysis1.at[i, 'Unadjusted CAGR'] / analysis1.at[i, 'Unadj Std Dev']

#second analysis dataframe follows same steps
#as the first, but on a 5 year basis
analysis2 = pd.DataFrame(columns = ['Adjusted CAGR', 'Adj Std Dev', 'Adj Max DD', 'Adj SSR', 'Unadjusted CAGR', 'Unadj Std Dev', 'Unadj Max DD', 'Unadj SSR'])
rowCount3 = len(analysis2.index)

std_calculator3 = pd.Series(dtype = 'float64')
std_calculator4 = pd.Series(dtype = 'float64')
maxDD3 = 0
maxDD4 = 0

for i in range(61, rowCount):
    analysis2.at[i, 'Adjusted CAGR'] = ((df.at[i, 'Adjusted Equity'] / df.at[i - 60, 'Adjusted Equity']) ** (1 / 5) - 1)
    analysis2.at[i, 'Unadjusted CAGR'] = ((df.at[i, 'Adjusted Equity'] / df.at[i - 60, 'Unadjusted Equity']) ** (1 / 5) - 1)

    std_calculator3.at[i] = analysis1.iloc[i, 0]
    analysis2.at[i, 'Adj Std Dev'] = std_calculator3.std()

    std_calculator4.at[i] = analysis1.iloc[i, 4]
    analysis2.at[i, 'Unadj Std Dev'] = std_calculator4.std()

    if df.at[i, 'DD Adjusted'] > maxDD3:
        maxDD3 = df.at[i, 'DD Adjusted']
    analysis2.at[i, 'Adj Max DD'] = maxDD3

    if df.at[i, 'DD Unadjusted'] > maxDD4:
        maxDD4 = df.at[i, 'DD Unadjusted']
    analysis2.at[i, 'Unadj Max DD'] = maxDD4

    analysis2.at[i, 'Adj SSR'] = analysis2.at[i, 'Adjusted CAGR'] / analysis1.at[i, 'Adj Std Dev']
    analysis2.at[i, 'Unadj SSR'] = analysis2.at[i, 'Unadjusted CAGR'] / analysis1.at[i, 'Unadj Std Dev']

#write dataframes to csv files
df.to_csv('new25.csv')
analysis1.to_csv('Summary1yr.csv')
analysis2.to_csv('Summary5yr.csv')

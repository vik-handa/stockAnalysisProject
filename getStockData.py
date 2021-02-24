from datetime import datetime
import requests, json
import pandas as pd
import matplotlib.pyplot as plt

#retrieve and format data
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
df.to_csv('old25.csv')

#Takes only the date and AdjClose Columns from the downloaded data
#and truncates the date to exclude the time
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

#Calculate equities, maximums, and CAGRs
for i in range(1, rowCount):
    df.at[i, 'Unadjusted Equity'] = (priceA * (df.iloc[i,2] + 1))
    priceA = df.at[i, 'Unadjusted Equity']
    if priceA > maxUnadj:
        maxUnadj = priceA

    df.at[i, 'Max Unadjusted'] = round(maxUnadj, 4)

    if df.at[i, 'In Market?']:
        df.at[i, 'Adjusted Equity'] = (priceB * (df.iloc[i, 2] + 1))
        priceB = df.at[i, 'Adjusted Equity']
    else:
        df.at[i, 'Adjusted Equity'] = priceB
        priceB = df.at[i, 'Adjusted Equity']

    if priceB > maxAdj:
        maxAdj = priceB

    df.at[i, 'Max Adjusted'] = round(maxAdj, 4)

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

print(df)
df.to_csv('new25.csv')

x = df['date']
y = df['Unadjusted Equity']
z = df['Adjusted Equity']

plt.plot(x,y)
plt.plot(x,z)
plt.show()

from datetime import datetime
import requests, json
import pandas as pd
import matplotlib.pyplot as plt

#retrieve and format data
token = '63753ff0e6fc15c8593da0ccaca6238f7b6abe6e'
Ticker = 'AAPL'
startDate = '1995-01-02'
headers = {
        'Content-Type': 'application/json',
        'Authorization' : 'Token ' + token
        }

requestResponse = requests.get('https://api.tiingo.com/tiingo/daily/'+ Ticker +'/prices?startDate=1995-01-02&endDate=2021-01-01&resampleFreq=monthly', headers=headers)

data = requestResponse.json()
df = pd.DataFrame(data)
df.to_csv('old25.csv')

df = df[['date', 'adjClose']]
rowCount = len(df.index)
for i in range(0, rowCount):
        val = df.at[i, 'date']
        df.at[i, 'date'] = val[:10]

#initialize columns as long type and name them
a = df['adjClose']
a = a.pct_change()

b = df['adjClose']
b = b.pct_change(periods=5)

c = [0.00]
c = pd.Series(c)

d = [0.00]
d = pd.Series(d)
truthVal = (a > 0) | (b > 0)
d = truthVal
d[0] = True
d[1] = True
d[2] = True

e = [0.00]
e = pd.Series(e)

f = [0.00]
f = pd.Series(e)

g = [0.00]
g = pd.Series(g)

h = [0.00]
h = pd.Series(h)

i = [0.00]
i = pd.Series(i)

j = [0.00]
j = pd.Series(j)

k = [0.00]
k = pd.Series(k)

l = [0.00]
l = pd.Series(l)

m = [0.00]
m = pd.Series(m)

n = [0.00]
n = pd.Series(n)

df['1 Month Change'] = a
df['5 Month Change'] = b
df['Unadjusted Equity'] = c
df['In Market?'] = d
df['Adjusted Equity'] = e
df['Adjusted CAGR'] = f
df['Unadjusted CAGR'] = g
df['Max Unadjusted'] = h
df['Max Adjusted'] = i
df['DD Unadjusted'] = j
df['DD Unadjusted Percentage'] = k
df['DD Adjusted'] = l
df['DD Unadjusted Percentage'] = m
df['Sharpe Ratio'] = n

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

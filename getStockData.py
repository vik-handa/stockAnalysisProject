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

#create dataframe to compare following variables for NONTIMER and TIMER
analysis1 = pd.DataFrame(columns = ['date', 'Adjusted Close', '1 Month Change', 'Monthly Change Std', 'Unadjusted Equity', 'Unadjusted CAGR', 'Max Equity', 'Dropdown', 'DD Percentage'])
analysis2 = pd.DataFrame(columns = ['date', 'Adjusted Close', '1 Month Change', 'Monthly Change Std', 'Adjusted Equity', 'Adjusted CAGR', 'Max Equity', 'Dropdown', 'DD Percentage'])

#copies general stock info (closing prices, equity, dropdowns, and dropdown percentage) from original dataframe
analysis1["date"] = df['date']
analysis1["Adjusted Close"] = df['adjClose']
analysis1['1 Month Change'] = df['1 Month Change']
analysis1['Unadjusted Equity'] = df['Unadjusted Equity']
analysis1['Max Equity'] = df['Max Unadjusted']
analysis1['Dropdown'] = df['DD Unadjusted']
analysis1['DD Percentage'] = df['DD Unadjusted Percentage']

#computes standard deviation of monthly change and CAGR over 25 year span
analysis1.at[0, 'Monthly Change Std'] = analysis1['1 Month Change'].std()
analysis1.at[0, 'Unadjusted CAGR'] = (analysis1['Unadjusted Equity'].iloc[-1] / analysis1['Unadjusted Equity'].iloc[0]) ** (1 / years) - 1

#copies general info again just as we did above
analysis2["date"] = df['date']
analysis2["Adjusted Close"] = df['adjClose']
analysis2['1 Month Change'] = df['Adjusted Equity']
analysis2['1 Month Change'] = round(analysis2['1 Month Change'].pct_change(), 4)
analysis2['Adjusted Equity'] = df['Adjusted Equity']
analysis2['Max Equity'] = df['Max Adjusted']
analysis2['Dropdown'] = df['DD Adjusted']
analysis2['DD Percentage'] = df['DD Adjusted Percentage']

#computes standard deviation of monthly change and CAGR over 25 year span
analysis2.at[0, 'Monthly Change Std'] = analysis2['1 Month Change'].std()
analysis2.at[0, 'Adjusted CAGR'] = (analysis2['Adjusted Equity'].iloc[-1] / analysis2['Adjusted Equity'].iloc[0]) ** (1 / years) - 1

#create dataframes to compare TIMER and NONTIMER results within 5 year intervals
rolling_unadjusted = pd.DataFrame(columns = ['Start Date', 'End Date', 'Std Dev', 'CAGR', 'Max Percentage DD', 'SSR'])
rolling_adjusted = pd.DataFrame(columns = ['Start Date', 'End Date', 'Std Dev', 'CAGR', 'Max Percentage DD', 'SSR', 'Helped?', 'Help Stats'])

#pandas series used to help calculate standard deviations and maximum drawdowns
std_calculator = pd.Series(dtype = 'float64')
maxDD_calculator = pd.Series(dtype = 'float64')

#fills out start date and end date columns for NONTIMER
#cuts off the last 5 rows (Not enough data for 5 year intervals after August 2020)
rolling_unadjusted['Start Date'] = df['date']
rolling_unadjusted['End Date'] = df['date']
rolling_unadjusted['End Date'] = rolling_unadjusted['End Date'].shift(periods = -60)
rolling_unadjusted = rolling_unadjusted[:-60]
interval_row_count = rowCount - 60

#for each interval
for i in range(0, interval_row_count):

    #add 5 monthly change values into series and find std dev
    #add 5 dropdown percentage values into series and find max
    for j in range(0,60):
        std_calculator.at[j] = analysis1.iloc[i + j, 2]
        maxDD_calculator.at[j] = analysis1.iloc[i + j, 8]
        maxDD_calculator.at[j] = analysis1.iloc[i + j, 8]
    rolling_unadjusted.at[i, 'Std Dev'] = round(std_calculator.std(), 4)
    rolling_unadjusted.at[i, 'Max Percentage DD'] = maxDD_calculator.min()

    #compute CAGR over 5 year span, rounded for clarity
    rolling_unadjusted.at[i, 'CAGR'] = round((analysis1.iloc[i + 60, 4] / analysis1.iloc[i, 4]) ** 0.2 - 1, 4)

#computes simplifies sharpe ratio for each interval
rolling_unadjusted['SSR'] = rolling_unadjusted['CAGR'] / rolling_unadjusted['Std Dev']


#copying dstock info again for intervals with TIMER
rolling_adjusted['Start Date'] = df['date']
rolling_adjusted['End Date'] = df['date']
rolling_adjusted['End Date'] = rolling_adjusted['End Date'].shift(periods = -60)
rolling_adjusted = rolling_adjusted[:-60]

#keeps track of number of intervals the timer helped
help_count = 0

#for each interval
for i in range(0, interval_row_count):

    #compute standard deviations and max of drawdown percentages
    for j in range(0,60):
        std_calculator.at[j] = analysis2.iloc[i + j, 2]
        maxDD_calculator.at[j] = analysis2.iloc[i + j, 8]
        maxDD_calculator.at[j] = analysis2.iloc[i + j, 8]
    rolling_adjusted.at[i, 'Std Dev'] = round(std_calculator.std(), 4)
    rolling_adjusted.at[i, 'Max Percentage DD'] = maxDD_calculator.min()

    #compute CAGRs for 5 year interval, rounded for clarity
    rolling_adjusted.at[i, 'CAGR'] = round((analysis2.iloc[i + 60, 4] / analysis2.iloc[i, 4]) ** 0.2 - 1, 4)
    if rolling_adjusted.at[i, 'Std Dev'] != 0:
        rolling_adjusted.at[i, 'SSR'] = rolling_adjusted.at[i, 'CAGR'] / rolling_adjusted.at[i, 'Std Dev']

    #fills out if the timer helps if timer either
    # improves sharpe ratio OR
    # improves CAGR and reduces max DD percentage
    if rolling_adjusted.at[i, 'SSR'] > rolling_unadjusted.at[i, 'SSR']:
        rolling_adjusted.at[i, 'Helped?'] = 'Yes'
        help_count += 1
    if rolling_adjusted.at[i, 'CAGR'] > rolling_unadjusted.at[i, 'CAGR'] and rolling_adjusted.at[i, 'Max Percentage DD'] < rolling_unadjusted.at[i, 'Max Percentage DD']:
        rolling_adjusted.at[i, 'Helped?'] = 'Yes'
        help_count += 1

# displays number of intervals helped and proportion of total intervals that were helped
rolling_adjusted.at[0, 'Help Stats'] = 'Number of Intervals Helped: ' + str(help_count)
rolling_adjusted.at[1, 'Help Stats'] = 'Proportion of Intervals Helped: ' + str(round(help_count / interval_row_count, 4))
print(rolling_adjusted)


#write dataframes to csv files
df.to_csv('new25.csv')
analysis1.to_csv('UnadjustedSummary.csv')
analysis2.to_csv('AdjustedSummary.csv')
rolling_unadjusted.to_csv('interval_no_timer.csv')
rolling_adjusted.to_csv('interval_timer.csv')

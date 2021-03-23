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
df = pd.read_csv('old25.csv')
df.to_csv('stockcheck1.csv')

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
        df.at[i, 'Adjusted CAGR'] = ((df.at[i, 'Adjusted Equity'] / 1000) ** (1 / years) - 1)
        df.at[i, 'Unadjusted CAGR'] = ((df.at[i, 'Unadjusted Equity'] / 1000) ** (1 / years) - 1)


#Calculate dropdowns and their percentages
df['DD Unadjusted'] = round(df['Max Unadjusted'] - df['Unadjusted Equity'], 4)
df['DD Unadjusted Percentage'] = round(df['DD Unadjusted'] / df['Max Unadjusted'], 4)
df['DD Adjusted'] = round(df['Max Adjusted'] - df['Adjusted Equity'], 4)
df['DD Adjusted Percentage'] = round(df['DD Adjusted'] / df['Max Adjusted'], 4)

#temporary fix to help readibility
df['Adjusted Equity'] = round(df['Adjusted Equity'], 4)
df['Unadjusted Equity'] = round(df['Unadjusted Equity'], 4)
df['1 Month Change'] = round(df['1 Month Change'], 4)
df['5 Month Change'] = round(df['5 Month Change'], 4)
df['adjClose'] = round(df['adjClose'], 4)

#create dataframe to compare following variables for NONTIMER and TIMER
analysis1 = pd.DataFrame(columns = ['date', 'Adjusted Close', '1 Month Change', 'Monthly Change Std', 'Unadjusted Equity', 'Unadjusted CAGR', 'Max Equity', 'Dropdown', 'DD Percentage'])
analysis2 = pd.DataFrame(columns = ['date', 'Adjusted Close', 'Adj 1 Month Change', 'Adj Monthly Change Std', 'Adjusted Equity', 'Adjusted CAGR', 'Adj Max Equity', 'Adj Dropdown', 'Adj DD Percentage'])

#copies general stock info (closing prices, equity, dropdowns, and dropdown percentage) from original dataframe
analysis1["date"] = df['date']
analysis1["Adjusted Close"] = df['adjClose']
analysis1['1 Month Change'] = df['1 Month Change']
analysis1['Unadjusted Equity'] = df['Unadjusted Equity']
analysis1['Max Equity'] = df['Max Unadjusted']
analysis1['Dropdown'] = df['DD Unadjusted']
analysis1['DD Percentage'] = df['DD Unadjusted Percentage']
analysis1['       '] = ""

#computes standard deviation of monthly change and CAGR over 25 year span
#analysis1.at[0, 'Monthly Change Std'] = analysis1['1 Month Change'].std()
#analysis1.at[0, 'Unadjusted CAGR'] = (analysis1['Unadjusted Equity'].iloc[-1] / analysis1['Unadjusted Equity'].iloc[0]) ** (1 / years) - 1

#copies general info again just as we did above
analysis2["date"] = df['date']
analysis2["Adjusted Close"] = df['adjClose']
analysis2['Adj 1 Month Change'] = df['Adjusted Equity']
analysis2['Adj 1 Month Change'] = round(analysis2['Adj 1 Month Change'].pct_change(), 4)
analysis2['Adjusted Equity'] = df['Adjusted Equity']
analysis2['Adj Max Equity'] = df['Max Adjusted']
analysis2['Adj Dropdown'] = df['DD Adjusted']
analysis2['Adj DD Percentage'] = df['DD Adjusted Percentage']

#computes standard deviation of monthly change and CAGR over 25 year span
#analysis2.at[0, 'Monthly Change Std'] = analysis2['1 Month Change'].std()
#analysis2.at[0, 'Adjusted CAGR'] = (analysis2['Adjusted Equity'].iloc[-1] / analysis2['Adjusted Equity'].iloc[0]) ** (1 / years) - 1

#create dataframes to compare TIMER and NONTIMER results within 5 year intervals
rolling_unadjusted = pd.DataFrame(columns = ['Start Date', 'End Date', 'Std Dev', 'CAGR', 'Max Percentage DD', 'SSR'])
rolling_adjusted = pd.DataFrame(columns = ['Start Date', 'End Date', 'Adj Std Dev', 'Adj CAGR', 'Adj Max Percentage DD', 'Adj SSR', 'Helped?', 'Help Stats'])

#pandas series used to help calculate standard deviations and maximum drawdowns
std_calculator = pd.Series(dtype = 'float64')
max_equity_calculator = pd.Series(dtype = 'float64')
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
    for j in range(0, 60):
        std_calculator.at[j] = analysis1.iloc[i + j, 2]
        max_equity_calculator.at[j] = analysis1.iloc[i + j, 4]
    interval_adjusted_max_equity = max_equity_calculator.max()
    for j in range(0, 60):
        maxDD_calculator.at[j] = (interval_adjusted_max_equity - analysis1.iloc[i + j, 4]) / interval_adjusted_max_equity
    rolling_unadjusted.at[i, 'Std Dev'] = round(std_calculator.std(), 4)
    rolling_unadjusted.at[i, 'Max Percentage DD'] = "-" + str(round(maxDD_calculator.max(), 4))

    #compute CAGR over 5 year span, rounded for clarity
    rolling_unadjusted.at[i, 'CAGR'] = round((analysis1.iloc[i + 59, 4] / analysis1.iloc[i, 4]) ** 0.2 - 1, 4)

#computes simplifies sharpe ratio for each interval
rolling_unadjusted['SSR'] = rolling_unadjusted['CAGR'] / rolling_unadjusted['Std Dev']

#used to take final table data from starting to every consecutive month to starting January each year
rolling_unadjusted_shortened = pd.DataFrame(rolling_unadjusted)
rolling_adjusted_shortened = pd.DataFrame(rolling_unadjusted)
rows_to_delete = []
for i in range(0, interval_row_count):
    if i % 12 == 0:
        continue
    rows_to_delete.append(i)

rolling_unadjusted_shortened = rolling_unadjusted.drop(index = rows_to_delete)
rolling_unadjusted_shortened = rolling_unadjusted_shortened.reset_index(drop=True)


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
        max_equity_calculator.at[j] = analysis2.iloc[i + j, 4]
    interval_adjusted_max_equity = max_equity_calculator.max()

    for j in range(0, 60):
        maxDD_calculator.at[j] = (interval_adjusted_max_equity - analysis2.iloc[i + j, 4]) / interval_adjusted_max_equity
    rolling_adjusted.at[i, 'Adj Std Dev'] = round(std_calculator.std(), 4)
    rolling_adjusted.at[i, 'Adj Max Percentage DD'] = "-" + str(round(maxDD_calculator.max(), 4))


    #compute CAGRs for 5 year interval, rounded for clarity
    rolling_adjusted.at[i, 'Adj CAGR'] = round((analysis2.iloc[i + 59, 4] / analysis2.iloc[i, 4]) ** 0.2 - 1, 4)
    if rolling_adjusted.at[i, 'Adj Std Dev'] != 0:
        rolling_adjusted.at[i, 'Adj SSR'] = rolling_adjusted.at[i, 'Adj CAGR'] / rolling_adjusted.at[i, 'Adj Std Dev']

rolling_adjusted_shortened = rolling_adjusted.drop(index=rows_to_delete)
rolling_adjusted_shortened = rolling_adjusted_shortened.reset_index(drop=True)

    #fills out if the timer helps if timer either
    # improves sharpe ratio OR
    # improves CAGR and reduces max DD percentage
for i in range(0, interval_row_count - len(rows_to_delete)):
    if rolling_adjusted_shortened.at[i, 'Adj SSR'] > rolling_unadjusted_shortened.at[i, 'SSR']:
        rolling_adjusted_shortened.at[i, 'Helped?'] = 'Yes'
        help_count += 1
    elif rolling_adjusted_shortened.at[i, 'Adj CAGR'] > rolling_unadjusted_shortened.at[i, 'CAGR'] and rolling_adjusted_shortened.at[i, 'Max Percentage DD'] < rolling_unadjusted_shortened.at[i, 'Max Percentage DD']:
        rolling_adjusted_shortened.at[i, 'Helped?'] = 'Yes'
        help_count += 1

# displays number of intervals helped and proportion of total intervals that were helped
rolling_adjusted_shortened.at[0, 'Help Stats'] = 'Number of Intervals Helped: ' + str(help_count)
rolling_adjusted_shortened.at[1, 'Help Stats'] = 'Proportion of Intervals Helped: ' + str(round(help_count / (interval_row_count - len(rows_to_delete)), 4))

#connects dataframes to create final table
#date dropped from one table since we only need one date column for reference
analysis2 = analysis2.drop(columns=['date'])

#cuts rows out of the full raw data to represent each of the interval's raw data
final_raw = pd.concat([analysis1, analysis2], axis = 1)
raw1 = final_raw[0:60]
raw2 = final_raw[12:72]
raw3 = final_raw[24:84]
raw4 = final_raw[36:96]
raw5 = final_raw[48:108]
raw6 = final_raw[60:120]
raw7 = final_raw[72:132]
raw8 = final_raw[84:144]
raw9 = final_raw[96:156]
raw10 = final_raw[108:168]
raw11 = final_raw[120:180]
raw12 = final_raw[132:192]
raw13 = final_raw[144:204]
raw14 = final_raw[156:216]
raw15 = final_raw[168:228]
raw16 = final_raw[180:240]
raw17 = final_raw[192:252]
raw18 = final_raw[204:264]
raw19 = final_raw[216:278]
raw20 = final_raw[228:290]
raw21 = final_raw[240:302]

#resets the indexes of the interval raw data
raw2 = raw2.reset_index(drop=True)
raw3 = raw3.reset_index(drop=True)
raw4 = raw4.reset_index(drop=True)
raw5 = raw5.reset_index(drop=True)
raw6 = raw6.reset_index(drop=True)
raw7 = raw7.reset_index(drop=True)
raw8 = raw8.reset_index(drop=True)
raw9 = raw9.reset_index(drop=True)
raw10 = raw10.reset_index(drop=True)
raw11 = raw11.reset_index(drop=True)
raw12 = raw12.reset_index(drop=True)
raw13 = raw13.reset_index(drop=True)
raw14 = raw14.reset_index(drop=True)
raw15 = raw15.reset_index(drop=True)
raw16 = raw16.reset_index(drop=True)
raw17 = raw17.reset_index(drop=True)
raw18 = raw18.reset_index(drop=True)
raw19 = raw19.reset_index(drop=True)
raw20 = raw20.reset_index(drop=True)
raw21 = raw21.reset_index(drop=True)

#For each interval, calculate its std dev and CAGR
rawdatafiles = [raw1, raw2, raw3, raw4, raw5, raw6, raw7, raw8, raw9, raw10, raw11, raw12, raw13, raw14, raw15, raw16,
                raw17, raw18, raw19, raw20, raw21]

years = 5
for interval in rawdatafiles:
    interval.at[0, 'Monthly Change Std'] = interval['1 Month Change'].std()
    interval.at[0, 'Unadjusted CAGR'] = (interval.at[59, 'Unadjusted Equity'] / interval.at[0, 'Unadjusted Equity']) ** (1 / years) - 1

    interval.at[0, 'Adj Monthly Change Std'] = interval['Adj 1 Month Change'].std()
    interval.at[0, 'Adjusted CAGR'] = (interval.at[59, 'Adjusted Equity'] / interval.at[0, 'Adjusted Equity']) ** (1 / years) - 1

#write interval raw data to csv files
raw1.to_csv('interval1_rawdata.csv')
raw2.to_csv('interval2_rawdata.csv')
raw3.to_csv('interval3_rawdata.csv')
raw4.to_csv('interval4_rawdata.csv')
raw5.to_csv('interval5_rawdata.csv')
raw6.to_csv('interval6_rawdata.csv')
raw7.to_csv('interval7_rawdata.csv')
raw8.to_csv('interval8_rawdata.csv')
raw9.to_csv('interval9_rawdata.csv')
raw10.to_csv('interval10_rawdata.csv')
raw11.to_csv('interval11_rawdata.csv')
raw12.to_csv('interval12_rawdata.csv')
raw13.to_csv('interval13_rawdata.csv')
raw14.to_csv('interval14_rawdata.csv')
raw15.to_csv('interval15_rawdata.csv')
raw16.to_csv('interval16_rawdata.csv')
raw17.to_csv('interval17_rawdata.csv')
raw18.to_csv('interval18_rawdata.csv')
raw19.to_csv('interval19_rawdata.csv')
raw20.to_csv('interval20_rawdata.csv')
raw21.to_csv('interval21_rawdata.csv')

#final table combines the summary for interval vs non ointerval data
#plus info on how timer helped
rolling_adjusted_shortened = rolling_adjusted_shortened.drop(columns=['Start Date', 'End Date'])
final_analysis = pd.concat([rolling_unadjusted_shortened, rolling_adjusted_shortened], axis = 1)

#write dataframes to csv files
df.to_csv('new25.csv')
analysis1.to_csv('UnadjustedSummary.csv')
analysis2.to_csv('AdjustedSummary.csv')
rolling_unadjusted.to_csv('interval_no_timer.csv')
rolling_adjusted.to_csv('interval_timer.csv')
final_analysis.to_csv('final_table.csv')
final_raw.to_csv('final_raw.csv')

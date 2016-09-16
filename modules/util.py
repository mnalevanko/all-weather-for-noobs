import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np

DEFAULT_VOL_WINDOW = 200 # a little less than a year 

def get_returns(ticker, start=datetime.datetime(1940, 1, 1), end=datetime.datetime.now(), period=1):
	df = web.DataReader(ticker, "yahoo", start, end)
	df['Returns'] = df['Adj Close'].pct_change(period)
	df['Log Returns'] = np.log(df['Adj Close']) - np.log(df['Adj Close'].shift(1))
	return df

 # we want variance so that when we sum, we can just do the straight sum
def get_annualized_variance_of_series(series, window=DEFAULT_VOL_WINDOW):
	window_std = np.std(series.tail(window))
	variance = window_std ** 2
	ann_var = variance * np.sqrt(252) # 252 is number of trading days in a year
	return ann_var
import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np

VOL_WINDOW = 200

def get_returns(ticker, start=datetime.datetime(1940, 1, 1), end=datetime.datetime.now(), period=5):
	df = web.DataReader(ticker, "yahoo", start, end)
	df['Weekly Returns'] = df['Adj Close'].pct_change(period)
	return df

def get_variance_of_series(series, window=VOL_WINDOW):
	return np.std(series.tail(window)) ** 2
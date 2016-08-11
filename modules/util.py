import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np

def get_returns(ticker, start, end, period=5):
	df = web.DataReader(ticker, "yahoo", start, end)
	df['Returns'] = df['Adj Close'].pct_change(period)
	return df
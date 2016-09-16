import pandas as pd
import pandas_datareader.data as web
import util
import datetime

def backtest(weight_dict, output=False):
	print "Backtesting..."
	new_weight_dict = weight_dict.copy()
	del new_weight_dict['Date'] 

	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()

	returns_dfs = []

	for ticker in new_weight_dict:
		df = util.get_returns(ticker, start, end, period=1)
		df['%s Returns' % ticker] = df['Returns']
		df = pd.DataFrame(df['%s Returns' % ticker])
		returns_dfs.append(df)

	merged_df = merge_dataframes_by_latest_start_date(returns_dfs)
	merged_df['Portfolio Returns'] = merged_df['%s Returns' % new_weight_dict.keys()[0]] * 0.0 # just set it to 0 

	for ticker in new_weight_dict:
		weight = new_weight_dict[ticker]
		merged_df['Portfolio Returns'] = merged_df['Portfolio Returns'] + weight * merged_df['%s Returns' % ticker]

	if (output): merged_df.to_csv("backtest_results.csv")


def merge_dataframes_by_latest_start_date(dfs):
	dfs_sorted_by_latest_start_dates = sorted(dfs, key=lambda x: x.index[0], reverse=True)
	merged_df = dfs_sorted_by_latest_start_dates[0]

	for i in range(1, len(dfs_sorted_by_latest_start_dates)):
		df = dfs_sorted_by_latest_start_dates[i]
		merged_df = merged_df.join(df)

	return merged_df
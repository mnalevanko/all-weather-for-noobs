import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np
import collections

import pdb
import sys
import modules.util as util
import modules.backtesting as backtesting
import pprint
from modules.ticker_settings import *

##### IMPLEMENTATION DETAILS ##### 
# First we need to equalize the volatility in each growth / inflation box 
# And then assign equal volatility weights to each
# 
# NOTE: we are not calculating sum of variances the statistically "correct" way
# by subtracting out covariance as well, since covariance itself is unstable over time

VOL_WINDOW = 252

def main():
	pp = pprint.PrettyPrinter(indent=4)

	# first get ticker price and volatility data
	ticker_data = get_ticker_data() 
	ticker_volatilities = get_ticker_volatilities(ticker_data)
	# then treat each group (like stocks) as its own portfolio and equalize volatility contributions
	asset_class_weights = get_asset_class_weights(ticker_volatilities)
	# then treat each box as its own portfolio and equalize volatility contributions
	box_weights = get_box_weights(ticker_volatilities, asset_class_weights) 
	# then treat each box as an asset itself in a four-asset portfolio and equalize contributions
	environment_weights = get_environment_weights(ticker_volatilities, asset_class_weights, box_weights) 
	# find individual asset weight by multiplying box_weights and environment_weights per my all weather configuration
	weight_dict = finalize_ticker_weights(asset_class_weights, environment_weights, box_weights)

	print "Box weights"
	pp.pprint(box_weights)
	print "Environment weights"
	pp.pprint(environment_weights)
	print "Final weights"
	pp.pprint(weight_dict)
	update_weight_file(weight_dict)

	backtesting.backtest(weight_dict, output=True) # yes, this is backtesting with weights we could have only known today, so it's not super rigorous

def update_weight_file(weight_dict):
	weights = pd.read_csv(WEIGHTS_FILE).T.to_dict().values()
	weights.append(weight_dict)
	weights = pd.DataFrame(weights)
	weights.to_csv(WEIGHTS_FILE, index=False)

# given a tuple of (label, value), return
# risk parity equalized {"label": weight}
def equalize_weights(tuples):
	tuples = [tup for tup in tuples if tup[1] != 0.0] # remove zero values
	num_args = len(tuples)

	if (num_args):
		last_vol = tuples[num_args-1][1]
		last_label = tuples[num_args-1][0]

		last_vol_over_other_vols = []
		for i in range(0, num_args-1): 
			curr_vol = tuples[i][1]
			last_vol_over_other_vols.append(last_vol/curr_vol)

		weight_n = 1.0 / (sum(last_vol_over_other_vols) + 1)
		weights_i = collections.defaultdict(lambda: 0.0)
		for i in range(0, num_args-1):
			curr_vol = tuples[i][1]
			curr_label = tuples[i][0]
			weights_i[curr_label] = (last_vol / curr_vol) * weight_n

		weights_i[last_label] = weight_n
		return weights_i
	else:
		return collections.defaultdict(lambda: 0.0)

def get_ticker_volatilities(ticker_data):
	ticker_volatilities = {}
	for ticker in ticker_data:
		ticker_volatilities[ticker] = util.get_variance_of_series(ticker_data[ticker]['Weekly Returns'], window=VOL_WINDOW)
	return ticker_volatilities

# environment_box: gf|gr|ir|if
def finalize_ticker_weights(asset_class_weights, environment_weights, box_weights):
	stocks_weight = environment_weights['gr'] * box_weights['gr']['stocks'] + environment_weights['if'] * box_weights['if']['stocks'] 
	commodities_weight = environment_weights['gr'] * box_weights['gr']['commodities'] + environment_weights['ir'] * box_weights['ir']['commodities']
	nominal_bonds_weight = environment_weights['gf'] * box_weights['gf']['nominal bonds'] + environment_weights['if'] * box_weights['if']['nominal bonds']
	inflation_weight = environment_weights['ir'] * box_weights['ir']['inflation-linked'] + environment_weights['gf'] * box_weights['gf']["inflation-linked"]
	em_credit_weight = environment_weights['ir'] * box_weights['ir']['EM credit'] + environment_weights['gr'] * box_weights['gr']["EM credit"]
	corporate_credit_weight = environment_weights['gr'] * box_weights['gr']['corporate credit']

	weights_by_asset = {
		"stocks": stocks_weight, 
		"commodities": commodities_weight, 
		"nominal bonds": nominal_bonds_weight,
		"inflation-linked": inflation_weight,
		"EM credit": em_credit_weight,
		"corporate credit": corporate_credit_weight
	}

	weights_dict = {}

	for asset_class in weights_by_asset:
		for ticker in TICKERS[asset_class]:
			weights_dict[ticker] = asset_class_weights[asset_class][ticker] * weights_by_asset[asset_class]

	weights_dict['Date'] = datetime.datetime.now().strftime("%m/%d/%y")

	return weights_dict

def get_ticker_data():
	# get all ticker price data -- we take the window of volatility 
	# in util.get_variance_of_series
	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()
	print "Getting ticker data..."

	ret = {}
	for group in TICKERS:
		for ticker in TICKERS[group]:
			ret[ticker] = util.get_returns(ticker, start=start, end=end)

	return ret

# return {asset_class: {tickers: weights}}
def get_asset_class_weights(ticker_volatilities):
	asset_class_weights = {}
	for asset_class in TICKERS: # stocks, commodities, EM credit, etc
		tickers_in_asset_class = TICKERS[asset_class]
		volatilities_for_tickers = [ticker_volatilities[ticker] for ticker in tickers_in_asset_class]
		ordered_weights_by_ticker = equalize_weights(zip(tickers_in_asset_class, volatilities_for_tickers)).values()
		asset_class_weights[asset_class] = dict(zip(tickers_in_asset_class, ordered_weights_by_ticker))

	return asset_class_weights

# return {"stocks": int, "commodities": int, etc} 
# @param: whatever is returend from get_asset_class_weights
def get_asset_class_volatilities_from_ticker_weights(asset_class_weights, ticker_volatilities):
	asset_volatilities = {}
	for asset_class in asset_class_weights:
		weights = asset_class_weights[asset_class]
		volatility = 0.0
		for ticker in weights:
			weight = weights[ticker]
			volatility += weight * ticker_volatilities[ticker]
		asset_volatilities[asset_class] = volatility
	return asset_volatilities

def get_box_weights(ticker_volatilities, asset_class_weights):
	asset_volatilities = get_asset_class_volatilities_from_ticker_weights(asset_class_weights, ticker_volatilities)

	# hacky i know but agh...
	def get_volatilities_tuples_if_exists(wanted_assets, asset_vol_dict): 
		return [(a, asset_vol_dict[a]) for a in wanted_assets if a in asset_vol_dict]

	# growth rising
	gr_weights = equalize_weights(get_volatilities_tuples_if_exists(['stocks', 'commodities', 'EM credit', 'corporate credit'], asset_volatilities))
	stocks_weight_gr = gr_weights['stocks']
	commodities_weight_gr = gr_weights['commodities']
	em_credit_weight_gr = gr_weights['EM credit']
	corp_credit_weight_gr = gr_weights['corporate credit']

	# growth falling
	gf_weights = equalize_weights(get_volatilities_tuples_if_exists(['nominal bonds', 'inflation-linked'], asset_volatilities))
	nominal_bonds_weight_gf = gf_weights['nominal bonds']
	inflation_weight_gf = gf_weights['inflation-linked']

	# inflation rising
	ir_weights = equalize_weights(get_volatilities_tuples_if_exists(['inflation-linked', 'commodities', 'EM credit'], asset_volatilities))
	inflation_weight_ir = ir_weights['inflation-linked']
	commodities_weight_ir = ir_weights['commodities']
	em_credit_weight_ir = ir_weights['EM credit']

	# inflation falling
	if_weights = equalize_weights(get_volatilities_tuples_if_exists(['stocks', 'nominal bonds'], asset_volatilities))
	stocks_weight_if = if_weights['stocks']
	nominal_bonds_weight_if = if_weights['nominal bonds']

	return {
		"gr": {"stocks": stocks_weight_gr, "commodities": commodities_weight_gr, "EM credit": em_credit_weight_gr, "corporate credit": corp_credit_weight_gr},
		"gf": {"nominal bonds": nominal_bonds_weight_gf, "inflation-linked": inflation_weight_gf},
		"ir": {"inflation-linked": inflation_weight_ir, "commodities": commodities_weight_ir, "EM credit": em_credit_weight_ir},
		"if": {"nominal bonds": nominal_bonds_weight_if, "stocks": stocks_weight_if},
	}

def get_environment_weights(ticker_volatilities, weights_per_asset_class, weights_per_box):
	asset_volatilities = get_asset_class_volatilities_from_ticker_weights(weights_per_asset_class, ticker_volatilities)
	gr_vol = weights_per_box['gr']['stocks'] * asset_volatilities['stocks'] \
			+ weights_per_box['gr']['commodities'] * asset_volatilities['commodities'] \
			+ weights_per_box['gr']['EM credit'] * asset_volatilities['EM credit'] \
			+ weights_per_box['gr']['corporate credit'] * asset_volatilities['corporate credit']
	gf_vol = weights_per_box['gf']['nominal bonds'] * asset_volatilities['nominal bonds'] \
			+ weights_per_box['gf']["inflation-linked"] * asset_volatilities["inflation-linked"]
	ir_vol = weights_per_box['ir']["inflation-linked"] * asset_volatilities["inflation-linked"] \
			+ weights_per_box['ir']['commodities'] * asset_volatilities['commodities'] \
			+ weights_per_box['ir']['EM credit'] * asset_volatilities['EM credit']
	if_vol = weights_per_box['if']['stocks'] * asset_volatilities['stocks'] \
			+ weights_per_box['if']['nominal bonds'] * asset_volatilities['nominal bonds']

	environment_weights = equalize_weights([('gr', gr_vol), ('gf', gf_vol), ('ir', ir_vol), ('if', if_vol)])
	gr_weight = environment_weights['gr']
	gf_weight = environment_weights['gf']
	ir_weight = environment_weights['ir']
	if_weight = environment_weights['if']

	return { 
		"gr": gr_weight,
		"gf": gf_weight,
		"ir": ir_weight,
		"if": if_weight
	}


if __name__ == "__main__":
	main()
import pandas as pd
import pandas_datareader.data as web
import datetime
import pdb
import numpy as np
import sys
import modules.util as util
import pprint

##### IMPLEMENTATION DETAILS ##### 
# All weather done with five assets:
# 1) VTI for stocks
# 2) DBC for growth commodities
# 3) TLT for nominal bonds
# 4) GLD for inflation-hedge commodities
# 
# First we need to equalize the volatility in each growth / inflation box 
# And then assign equal volatility weights to each
# 
# NOTE: we are not calculating sum of variances the statistically "correct" way
# by subtracting out covariance as well, since covariance itself is unstable over time

WEIGHTS_FILE = "weights.csv"
TICKERS = {"stocks": ['VTI', 'VGK', 'VWO'], "commodities": ['DBC'], "nominal bonds": ['TLT'], "inflation": ['GLD']}

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
	print pp.pprint(box_weights)
	print "Environment weights"
	print pp.pprint(environment_weights)
	print "Final weights"
	pp.pprint(weight_dict)

	update_weight_file(weight_dict)

def update_weight_file(weight_dict):
	weights = pd.read_csv(WEIGHTS_FILE).T.to_dict().values()
	weights.append(weight_dict)

	weights = pd.DataFrame(weights)
	weights.to_csv(WEIGHTS_FILE, index=False)

def equalize_weights(args):
	num_args = len(args)
	last_vol = args[num_args-1]

	last_vol_over_other_vols = []
	for i in range(0, num_args-1): 
		last_vol_over_other_vols.append(last_vol/args[i])

	weight_n = 1.0 / (sum(last_vol_over_other_vols) + 1)
	weights_i = []
	for i in range(0, num_args-1):
		weights_i.append((last_vol / args[i]) * weight_n)

	weights_i.append(weight_n)
	return weights_i

def get_ticker_volatilities(ticker_data):
	ticker_volatilities = {}
	for ticker in ticker_data:
		ticker_volatilities[ticker] = util.get_variance_of_series(ticker_data[ticker]['Weekly Returns'])
	return ticker_volatilities

# environment_box: gf|gr|ir|if
def finalize_ticker_weights(asset_class_weights, environment_weights, box_weights):
	stocks_weight = environment_weights['gr'] * box_weights['gr']['stocks'] + environment_weights['if'] * box_weights['if']['stocks'] 
	commodities_weight = environment_weights['gr'] * box_weights['gr']['commodities'] + environment_weights['ir'] * box_weights['ir']['commodities']
	nominal_bonds_weight = environment_weights['gf'] * box_weights['gf']['nominal bonds'] + environment_weights['if'] * box_weights['if']['nominal bonds']
	inflation_weight = environment_weights['ir'] * box_weights['ir']['inflation'] + environment_weights['gf'] * box_weights['gf']['inflation']

	weights_by_asset = {
		"stocks": stocks_weight, 
		"commodities": commodities_weight, 
		"nominal bonds": nominal_bonds_weight,
		"inflation": inflation_weight
	}

	weights_dict = {}

	for asset_class in weights_by_asset:
		for ticker in TICKERS[asset_class]:
			weights_dict[ticker] = asset_class_weights[asset_class][ticker] * weights_by_asset[asset_class]

	return weights_dict

def get_ticker_data():
	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()
	print "Getting ticker data..."

	ret = {}
	for group in TICKERS:
		for ticker in TICKERS[group]:
			ret[ticker] = util.get_returns(ticker, start, end)

	return ret

# return {asset_class: {tickers: weights}}
def get_asset_class_weights(ticker_volatilities):
	asset_class_weights = {}
	for asset_class in TICKERS:
		tickers_in_asset_class = TICKERS[asset_class]
		volatilities_for_tickers = [ticker_volatilities[ticker] for ticker in tickers_in_asset_class]
		ordered_weights_by_ticker = equalize_weights(volatilities_for_tickers)
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

	# growth rising
	gr_weights = equalize_weights([asset_volatilities['stocks'], asset_volatilities['commodities']])
	stocks_weight_gr = gr_weights[0]
	commodities_weight_gr = gr_weights[1]

	# growth falling
	gf_weights = equalize_weights([asset_volatilities['nominal bonds'], asset_volatilities['inflation']])
	nominal_bonds_weight_gf = gf_weights[0]
	inflation_weight_gf = gf_weights[1]

	# inflation rising
	ir_weights = equalize_weights([asset_volatilities['inflation'], asset_volatilities['commodities']])
	inflation_weight_ir = ir_weights[0]
	commodities_weight_ir = ir_weights[1]

	# inflation falling
	if_weights = equalize_weights([asset_volatilities['stocks'], asset_volatilities['nominal bonds']])
	stocks_weight_if = if_weights[0]
	nominal_bonds_weight_if = if_weights[1]

	return {
		"gr": {"stocks": stocks_weight_gr, "commodities": commodities_weight_gr},
		"gf": {"nominal bonds": nominal_bonds_weight_gf, "inflation": inflation_weight_gf},
		"ir": {"inflation": inflation_weight_ir, "commodities": commodities_weight_ir},
		"if": {"nominal bonds": nominal_bonds_weight_if, "stocks": stocks_weight_if},
	}

def get_environment_weights(ticker_volatilities, weights_per_asset_class, weights_per_box):
	asset_volatilities = get_asset_class_volatilities_from_ticker_weights(weights_per_asset_class, ticker_volatilities)

	gr_vol = weights_per_box['gr']['stocks'] * asset_volatilities['stocks'] \
			+ weights_per_box['gr']['commodities'] * asset_volatilities['commodities']
	gf_vol = weights_per_box['gf']['nominal bonds'] * asset_volatilities['nominal bonds'] \
			+ weights_per_box['gf']['inflation'] * asset_volatilities['inflation']
	ir_vol = weights_per_box['ir']['inflation'] * asset_volatilities['inflation'] \
			+ weights_per_box['ir']['commodities'] * asset_volatilities['commodities']
	if_vol = weights_per_box['if']['stocks'] * asset_volatilities['stocks'] \
			+ weights_per_box['if']['nominal bonds'] * asset_volatilities['nominal bonds']

	environment_weights = equalize_weights([gr_vol, gf_vol, ir_vol, if_vol])
	gr_weight = environment_weights[0]
	gf_weight = environment_weights[1]
	ir_weight = environment_weights[2]
	if_weight = environment_weights[3]

	return { 
		"gr": gr_weight,
		"gf": gf_weight,
		"ir": ir_weight,
		"if": if_weight
	}


if __name__ == "__main__":
	main()
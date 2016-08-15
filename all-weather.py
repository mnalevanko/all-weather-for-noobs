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
TICKERS = ['VTI', 'DBC', 'TLT', 'GLD', 'HYG']
VOL_WINDOW = 200


def main():
	pp = pprint.PrettyPrinter(indent=4)

	ticker_data = get_ticker_data() # first get ticker data
	box_weights = get_box_weights(ticker_data) # then treat each box as its own portfolio and equalize volatility contributions
	environment_weights = get_environment_weights(ticker_data, box_weights) # then treat each box as an asset itself in a four-asset portfolio and equalize contributions

	print "Box weights"
	print pp.pprint(box_weights)
	print "Environment weights"
	print pp.pprint(environment_weights)

	# find individual asset weight by multiplying box_weights and environment_weights per my all weather configuration
	vti_weight = environment_weights['gr'] * box_weights['gr']['VTI'] + environment_weights['if'] * box_weights['if']['VTI'] 
	dbc_weight = environment_weights['gr'] * box_weights['gr']['DBC'] + environment_weights['ir'] * box_weights['ir']['DBC']
	tlt_weight = environment_weights['gf'] * box_weights['gf']['TLT'] + environment_weights['if'] * box_weights['if']['TLT']
	gld_weight = environment_weights['ir'] * box_weights['ir']['GLD'] + environment_weights['gf'] * box_weights['gf']['GLD']
	
	hyg_weight = environment_weights['gr'] * box_weights['gr']['HYG'] 

	weight_dict = {
		"Date": datetime.datetime.now().strftime("%m/%d/%y"),
		"VTI": vti_weight,
		"DBC": dbc_weight,
		"TLT": tlt_weight,
		"GLD": gld_weight,
		"HYG": hyg_weight
	}

	print "Final weights"
	pp.pprint(weight_dict)

	# update weight file
	weights = pd.read_csv(WEIGHTS_FILE).T.to_dict().values()
	weights.append(weight_dict)

	weights = pd.DataFrame(weights)
	weights.to_csv(WEIGHTS_FILE, index=False)

def equalize_weights(*args):
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

def get_ticker_data():
	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()
	print "Getting ticker data..."

	ret = {}
	for ticker in TICKERS:
		ret[ticker] = util.get_returns(ticker, start, end)

	return ret

def get_variance_of_series(series, window=VOL_WINDOW):
	return np.std(series.tail(window)) ** 2

def get_box_weights(ticker_dfs):
	vti_vol = get_variance_of_series(ticker_dfs['VTI']['Returns'])
	dbc_vol = get_variance_of_series(ticker_dfs['DBC']['Returns'])
	tlt_vol = get_variance_of_series(ticker_dfs['TLT']['Returns'])
	gld_vol = get_variance_of_series(ticker_dfs['GLD']['Returns'])

	hyg_vol = get_variance_of_series(ticker_dfs['HYG']['Returns'])

	# growth rising
	gr_weights = equalize_weights(vti_vol, dbc_vol, hyg_vol)
	vti_weight_gr = gr_weights[0]
	dbc_weight_gr = gr_weights[1]
	hyg_weight_gr = gr_weights[2]

	# growth falling
	gf_weights = equalize_weights(tlt_vol, gld_vol)
	tlt_weight_gf = gf_weights[0]
	gld_weight_gf = gf_weights[1]

	# inflation rising
	ir_weights = equalize_weights(gld_vol, dbc_vol)
	gld_weight_ir = ir_weights[0]
	dbc_weight_ir = ir_weights[1]

	# inflation falling
	if_weights = equalize_weights(vti_vol, tlt_vol)
	vti_weight_if = if_weights[0]
	tlt_weight_if = if_weights[1]

	return {
		"gr": {"VTI": vti_weight_gr, "DBC": dbc_weight_gr, "HYG": hyg_weight_gr},
		"gf": {"TLT": tlt_weight_gf, "GLD": gld_weight_gf},
		"ir": {"GLD": gld_weight_ir, "DBC": dbc_weight_ir},
		"if": {"TLT": tlt_weight_if, "VTI": vti_weight_if},
	}

def get_environment_weights(ticker_dfs, weights_per_box):
	vti_vol = get_variance_of_series(ticker_dfs['VTI']['Returns'])
	dbc_vol = get_variance_of_series(ticker_dfs['DBC']['Returns'])
	tlt_vol = get_variance_of_series(ticker_dfs['TLT']['Returns'])
	gld_vol = get_variance_of_series(ticker_dfs['GLD']['Returns'])

	hyg_vol = get_variance_of_series(ticker_dfs['HYG']['Returns'])

	gr_vol = weights_per_box['gr']['VTI'] * vti_vol + weights_per_box['gr']['DBC'] * dbc_vol + weights_per_box['gr']['HYG'] * hyg_vol
	gf_vol = weights_per_box['gf']['TLT'] * tlt_vol + weights_per_box['gf']['GLD'] * gld_vol
	ir_vol = weights_per_box['ir']['GLD'] * gld_vol + weights_per_box['ir']['DBC'] * dbc_vol 
	if_vol = weights_per_box['if']['VTI'] * vti_vol + weights_per_box['if']['TLT'] * tlt_vol

	environment_weights = equalize_weights(gr_vol, gf_vol, ir_vol, if_vol)
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
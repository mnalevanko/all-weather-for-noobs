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
TICKERS = ['VTI', 'DBC', 'TLT', 'GLD']
VOL_WINDOW = 200

def get_ticker_data():
	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()
	print "Getting ticker data..."

	ret = {}
	for ticker in TICKERS:
		ret[ticker] = util.get_returns(ticker, start, end)

	return ret		

def get_box_weights(ticker_dfs):

	def equalize_weights_for_two_vars(v1, v2):
		v1_weight = (v2) / (v1 + v2)
		v2_weight = (v1) / (v1 + v2)
		return v1_weight, v2_weight

	vti_vol = np.std(ticker_dfs['VTI']['Returns'].tail(VOL_WINDOW)) ** 2
	dbc_vol = np.std(ticker_dfs['DBC']['Returns'].tail(VOL_WINDOW)) ** 2
	tlt_vol = np.std(ticker_dfs['TLT']['Returns'].tail(VOL_WINDOW)) ** 2
	gld_vol = np.std(ticker_dfs['GLD']['Returns'].tail(VOL_WINDOW)) ** 2

	# growth rising
	vti_weight_gr, dbc_weight_gr = equalize_weights_for_two_vars(vti_vol, dbc_vol)

	# growth falling
	tlt_weight_gf, gld_weight_gf = equalize_weights_for_two_vars(tlt_vol, gld_vol)

	# inflation rising
	gld_weight_ir, dbc_weight_ir = equalize_weights_for_two_vars(gld_vol, dbc_vol)

	# inflation falling
	vti_weight_if, tlt_weight_if = equalize_weights_for_two_vars(vti_vol, tlt_vol)

	return {
		"gr": {"VTI": vti_weight_gr, "DBC": dbc_weight_gr},
		"gf": {"TLT": tlt_weight_gf, "GLD": gld_weight_gf},
		"ir": {"GLD": gld_weight_ir, "DBC": dbc_weight_ir},
		"if": {"TLT": tlt_weight_if, "VTI": vti_weight_if},
	}

def get_environment_weights(ticker_dfs, weights_per_box):
	def equalize_weights_for_four_vars(v1, v2, v3, v4):
		# probably a problem with the math here
		w4 = (v1 * v2 * v3) / (v1 * v2 * v3 + v4 * v2 * v3 + v4 * v1 * v3 + v4 * v1 * v2)
		w1 = (v4 / v1) * w4
		w2 = (v4 / v2) * w4
		w3 = (v4 / v3) * w4
		return w1, w2, w3, w4

	vti_vol = np.std(ticker_dfs['VTI']['Returns'].tail(VOL_WINDOW)) ** 2
	dbc_vol = np.std(ticker_dfs['DBC']['Returns'].tail(VOL_WINDOW)) ** 2
	tlt_vol = np.std(ticker_dfs['TLT']['Returns'].tail(VOL_WINDOW)) ** 2
	gld_vol = np.std(ticker_dfs['GLD']['Returns'].tail(VOL_WINDOW)) ** 2

	gr_vol = weights_per_box['gr']['VTI'] * vti_vol + weights_per_box['gr']['DBC'] * dbc_vol
	gf_vol = weights_per_box['gf']['TLT'] * tlt_vol + weights_per_box['gf']['GLD'] * gld_vol
	ir_vol = weights_per_box['ir']['GLD'] * gld_vol + weights_per_box['ir']['DBC'] * dbc_vol
	if_vol = weights_per_box['if']['VTI'] * vti_vol + weights_per_box['if']['TLT'] * tlt_vol

	gr_weight, gf_weight, ir_weight, if_weight = \
			equalize_weights_for_four_vars(gr_vol, gf_vol, ir_vol, if_vol)

	return { 
		"gr": gr_weight,
		"gf": gf_weight,
		"ir": ir_weight,
		"if": if_weight
	}

def main():
	pp = pprint.PrettyPrinter(indent=4)

	ticker_data = get_ticker_data()
	box_weights = get_box_weights(ticker_data)
	environment_weights = get_environment_weights(ticker_data, box_weights)

	print "Box weights"
	print pp.pprint(box_weights)
	print "Environment weights"
	print pp.pprint(environment_weights)

	vti_weight = environment_weights['gr'] * box_weights['gr']['VTI'] + environment_weights['if'] * box_weights['if']['VTI']
	dbc_weight = environment_weights['gr'] * box_weights['gr']['DBC'] + environment_weights['ir'] * box_weights['ir']['DBC']
	tlt_weight = environment_weights['gf'] * box_weights['gf']['TLT'] + environment_weights['if'] * box_weights['if']['TLT']
	gld_weight = environment_weights['ir'] * box_weights['ir']['GLD'] + environment_weights['gf'] * box_weights['gf']['GLD']

	weight_dict = {
		"Date": datetime.datetime.now().strftime("%m/%d/%y"),
		"VTI": vti_weight,
		"DBC": dbc_weight,
		"TLT": tlt_weight,
		"GLD": gld_weight,
	}

	print "Final weights"
	pp.pprint(weight_dict)

	weights = pd.read_csv(WEIGHTS_FILE).T.to_dict().values()
	weights.append(weight_dict)

	weights = pd.DataFrame(weights)
	weights.to_csv(WEIGHTS_FILE, index=False)


main()
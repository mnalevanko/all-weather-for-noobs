WEIGHTS_FILE_TIER1 = "output/weights_tier1.csv"
WEIGHTS_FILE_TIER2 = "output/weights_tier2.csv"
WEIGHTS_FILE_TIER3 = "output/weights_tier3.csv"

TICKERS = {
	"stocks": ['VTI', 'VWO', 'VGK'], 
	"commodities": ['DBC'], 
	"corporate credit": ['HYG'],
	'EM credit': [],  # empty for now, can add
	"nominal bonds": ['TLT'], 
	"inflation-linked": ['GLD']
}

TIER_1_TICKERS = TICKERS.copy() 
TIER_2_TICKERS = TICKERS.copy()
TIER_2_TICKERS['corporate credit'] = []
TIER_3_TICKERS = TICKERS.copy()
TIER_3_TICKERS['corporate credit'] = []
TIER_3_TICKERS['stocks'] = ['VTI']

###############################################
# INPUT HERE
###############################################

WEIGHTS_FILE = WEIGHTS_FILE_TIER1
TICKERS = TIER_1_TICKERS
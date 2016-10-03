from modules.implied_vol import *

WEIGHTS_FILE_TIER1 = "output/weights_tier1.csv"
WEIGHTS_FILE_TIER2 = "output/weights_tier2.csv"
WEIGHTS_FILE_TIER3 = "output/weights_tier3.csv"
WEIGHTS_FILE_TIER4 = "output/weights_tier3_stocks_only_with_VGK.csv"
WEIGHTS_FILE_TIER5 = "output/weights_tier3_VGK_HYG.csv"

TICKERS = {
	"stocks": ['VTI', 'VWO', 'VGK'], 
	"commodities": ['DBC'], 
	"corporate credit": ['HYG'],
	'EM credit': [],  # empty for now, can add
	"nominal bonds": ['TLT'], 
	"inflation-linked": ['GLD']
}

# VTI, VWO, VGK, DBC, HYG, TLT, GLD
TIER_1_TICKERS = TICKERS.copy() 

# VTI, VWO, VGK, DBC, TLT, GLD
TIER_2_TICKERS = TICKERS.copy()
TIER_2_TICKERS['corporate credit'] = []

# VTI, DBC, TLT, GLD
TIER_3_TICKERS = TICKERS.copy()
TIER_3_TICKERS['corporate credit'] = []
TIER_3_TICKERS['stocks'] = ['VTI']

# VTI, VGK, TLT, GLD, DBC
TIER_4_TICKERS = TICKERS.copy()
TIER_4_TICKERS['corporate credit'] = []
TIER_4_TICKERS['stocks'] = ['VTI', 'VGK']

# VTI, VGK, HYG, TLT, GLD, DBC
TIER_5_TICKERS = TICKERS.copy()
TIER_5_TICKERS['stocks'] = ['VTI', 'VGK']

TICKER_TIERS = [
	(TIER_1_TICKERS, WEIGHTS_FILE_TIER1), 
	(TIER_2_TICKERS, WEIGHTS_FILE_TIER2), 
	(TIER_3_TICKERS, WEIGHTS_FILE_TIER3),
	(TIER_4_TICKERS, WEIGHTS_FILE_TIER4),
	(TIER_5_TICKERS, WEIGHTS_FILE_TIER5)
]

###############################################
# INPUT HERE

TIER_CHOICE = 5
TICKER_VOLATILITY_OVERRIDES = get_implied_volatilities_for_tickers(['TLT', 'GLD', 'DBC', 'HYG', 'VTI', 'VWO', 'VGK'])
VOL_WINDOW = 252

###############################################

TICKERS = TICKER_TIERS[TIER_CHOICE-1][0]
WEIGHTS_FILE = TICKER_TIERS[TIER_CHOICE-1][1]

print ">> Outputting to %s" % WEIGHTS_FILE
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

TICKER_TIERS = [(TIER_1_TICKERS, WEIGHTS_FILE_TIER1), (TIER_2_TICKERS, WEIGHTS_FILE_TIER2), (TIER_3_TICKERS, WEIGHTS_FILE_TIER3)]

###############################################
# INPUT HERE

TICKER_VOLATILITY_OVERRIDES = {}
TIER_CHOICE = 3

VOL_WINDOW = 60

###############################################

TICKERS = TICKER_TIERS[TIER_CHOICE-1][0]
WEIGHTS_FILE = TICKER_TIERS[TIER_CHOICE-1][1]

print ">> Outputting to %s" % WEIGHTS_FILE
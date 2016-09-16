from bs4 import BeautifulSoup
import requests
import numpy as np

# implied volatility is, in industry, usually in terms of annualized standard deviation
def get_implied_volatility_for_ticker(ticker):
	def remove_non_ascii_chars(string):
		return ''.join(i for i in string if ord(i)<128)

	url = "http://www.optionistics.com/quotes/stock-quotes/%s" % ticker
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'lxml')
	table = soup.find("div", {"class": "quotem"}).table
	rows = table.findAll("tr")

	for row in rows:
		if "IMPLIED VOLATILITY" in row.text: 
			all_tds = row.findAll("td")
			for i, td in enumerate(all_tds):
				if "IMPLIED VOLATILITY" in td.text:
					td_with_val = all_tds[i+1]
					text = remove_non_ascii_chars( td_with_val.getText() )
					return float(text)

def get_implied_volatilities_for_tickers(tickers, get_variance=True):
	ret = {}
	for ticker in tickers: 
		implied_vol = get_implied_volatility_for_ticker(ticker)
		if (get_variance): implied_vol = convert_annualized_stddev_to_annualized_variance(implied_vol)
		ret[ticker] = implied_vol
	return ret

def convert_annualized_stddev_to_annualized_variance(ann_std):
	variance = (ann_std / np.sqrt(252)) ** 2 
	return variance * np.sqrt(252)

if __name__ == "__main__":
	print get_implied_volatilities_for_tickers(['TLT', 'GLD', 'DBC', 'HYG', 'VTI', 'VWO', 'VGK'])
	print get_implied_volatilities_for_tickers(['TLT', 'GLD', 'DBC', 'HYG', 'VTI', 'VWO', 'VGK'], get_variance = False)
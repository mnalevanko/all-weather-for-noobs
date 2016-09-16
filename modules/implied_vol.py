from bs4 import BeautifulSoup
import requests

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

def get_implied_volatilities_for_tickers(tickers, get_variance = True):
	ret = {}
	for ticker in tickers: 
		implied_vol = get_implied_volatility_for_ticker(ticker)
		if (get_variance): implied_vol = implied_vol ** 2
		ret[ticker] = implied_vol
	return ret

if __name__ == "__main__":
	print get_implied_volatilities_for_tickers(['TLT', 'GLD', 'DBC', 'HYG', 'VTI', 'VWO', 'VGK'])
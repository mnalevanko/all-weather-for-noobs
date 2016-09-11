<h1>The Poor Man's All Weather Strategy</h1>

<h2> Obligatory Disclaimer </h2>

TL;DR Listen here buddy don't go out and log into your little brokerage account and start trading this strategy and then when you lose money come blaming me for it.

This code is developed for academic and illustrative purposes only and shall not be construed as financial, tax or legal advice or recommendations. The accuracy of the data on this site cannot be guaranteed. Users should use the information provided at their own risk and should always do their own due diligence before any investment decision. The information on this site does not constitute a solicitation for the purchase or sale of securities. No representation or implication is being made that using the information provided here will generate profits or ensure freedom from losses. All ideas and material presented are entirely those of the author and do not necessarily reflect those of the publisher. 

CFTC RULE 4.41 – HYPOTHETICAL OR SIMULATED PERFORMANCE RESULTS HAVE CERTAIN LIMITATIONS. UNLIKE AN ACTUAL PERFORMANCE RECORD, SIMULATED RESULTS DO NOT REPRESENT ACTUAL TRADING. ALSO, SINCE THE TRADES HAVE NOT BEEN EXECUTED, THE RESULTS MAY HAVE UNDER-OR-OVER COMPENSATED FOR THE IMPACT, IF ANY, OF CERTAIN MARKET FACTORS, SUCH AS LACK OF LIQUIDITY. SIMULATED TRADING PROGRAMS IN GENERAL ARE ALSO SUBJECT TO THE FACT THAT THEY ARE DESIGNED WITH THE BENEFIT OF HINDSIGHT. NO REPRESENTATION IS BEING MADE THAT ANY ACCOUNT WILL OR IS LIKELY TO ACHIEVE PROFIT OR LOSSES SIMILAR TO THOSE SHOWN.

<h2> Why All Weather? </h2>

(This section is still under development). 

Will probably need to fill this out a little more but the gist is that the smart and nice people at Wealthfront and related services use some assumptions and premises that are pretty wack -- for example:

<ul>
	<li> Assumptions of stable covariance (stocks and bonds are not always negatively correlated) </li>
	<li> Expected return assumptions a la capital asset pricing (often inaccurate) </li>
	<li> Less theoretically, they assume that "risk tolerance" is proportional to percentage of stocks you own </li>
</ul>

All Weather, on the other hand, does not make any covariance or expected return assumptions. It also does not equate stock ownership with risk tolerance. 

This strategy was developed and is used by Bridgewater Associates, a macro hedge fund in Connecticut. You can read about the theory behind this strategy <a href="http://www.bwater.com/research-library/the-all-weather-strategy/">here</a> and <a href="http://www.bwater.com/research-library/risk-parity/">here</a>.

It's worth making clear that this work represents my interpretation of publically available documents on Bridgewater's All Weather strategy and their approach to risk parity. They are not identical, nor did I receive or use any classified information during my time at Bridgewater that aided me in my work here.

<h2> Assumptions </h2>

In no particular order and subject to revision:

<ul>
	<li> Equalized variance within boxes before equalizing variance between boxes </li>
	<li> Didn't sum variances the statistically correct way because correlations between assets are inherently unstable </li>
	<li> Used four ETFs -- GLD (gold), DBC (commodities), TLT (long-term treasuries), and VTI (American stock market) </li>
	<li> The point of using these ETFs is that they all have roughly similar volatilities (as measured by standard deviation). I didn't double check to make sure that they have the same returns (and thus the same risk/return profiles) since I only have data going back 8-10 years</li>
	<li> I did not include an IL bond asset because there were no IL ETFs that were volatile enough or levered to work out. Gold is an (imperfect) substitute for this. </li>
</ul>

The All Weather configuration was as such (and also subject to revision):

<ul> 
	<li>Growth Rising: VTI, DBC (may also want to add EMB for EM debt and HYG for corporate debt)</li>
	<li>Growth Falling: TLT, GLD</li>
	<li>Inflation Rising: GLD, DBC, (may also want to add EMB for EM debt)</li>
	<li>Inflation Falling: VTI, TLT</li>
</ul>

<h2> Navigating the Files </h2>

There are two separate things to be aware of here: the research workflow, which is a mix of Excel and Python, and the output workflow, which is the systematization of insights gained from research.

The research workflow is something like this:

<ol>
	<li> Use series_getter.py to download price data for ETFs from Yahoo! Finance. This will output them to CSV, which I copied and pasted over to data/all-weather.xlsx</li>
	<li> Do whatever analysis in all-weather.xlsx. Use the "Simulated Returns" column to weight each asset however you'd like in a back-of-the-envelope manner. </li>
	<li> Copy and paste this column over to backtest/aw-simulated-returns.csv </li>
	<li> Use comparison.py to get the SP500's price data and remove #N/As from aw-simulated returns. Output these to two new files. </li>
	<li> Plot them in aw-simulated-returns.xlsx. </li>
</ol>

(Yeah yeah I know this is pretty nooby, judge me).

This is all completely separate from all-weather.py in the main folder, which takes the results of all the above research and systematizes it to spit out weights for the future, based on the last X days' volatilities for each ETF. It also outputs 
rough backtests.
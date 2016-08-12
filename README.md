<h1>The Poor Man's All Weather Strategy</h1>

<h2> Why All Weather? </h2>

Gonna fill out this section at some point

<h2> Assumptions </h2>

In no particular order and subject to revision:

<ul>
	<li> Equalized variance within boxes before equalizing variance between boxes </li>
	<li> Didn't sum variances the statistically correct way because "correlation doesn't exist" </li>
	<li> Used four ETFs -- GLD (gold), DBC (commodities), TLT (long-term treasuries), and VTI (American stock market) </li>
	<li> I did not include an IL bond asset because there were no IL ETFs that were volatile enough or levered to work out. Gold is an (imperfect) substitute for this. </li>
</ul>

The All Weather configuration was as such (and also subject to revision):

<ul> 
	<li>Growth Rising: VTI, DBC</li>
	<li>Growth Falling: TLT, but should probably also include gold for the inflation</li>
	<li>Inflation Rising: GLD, but should also probably include commodities </li>
	<li>Inflation Falling: VTI, TLT</li>
</ul>


<h2> Navigating the Files </h2>

The workflow is something like this: 

<ol>
	<li> Use series_getter.py to download price data for ETFs from Yahoo! Finance. This will output them to CSV, which I copied and pasted over to data/all-weather.xlsx</li>
	<li> Do whatever analysis in all-weather.xlsx. Use the "Simulated Returns" column to weight each asset however you'd like in a back-of-the-envelope manner. </li>
	<li> Copy and paste this column over to backtest/aw-simulated-returns.csv </li>
	<li> Use comparison.py to get the SP500's price data and remove #N/As from aw-simulated returns. Output these to two new files. </li>
	<li> Plot them in aw-simulated-returns.xlsx. </li>
</ol>

This is all completely separate from all-weather.py in the main folder, which takes the results of all the above research and systematizes it to spit out weights for the future, based on the last X days' volatilities for each ETF.
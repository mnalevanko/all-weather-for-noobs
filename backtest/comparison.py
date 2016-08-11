import pandas as pd
import pandas_datareader.data as web
import datetime
import pdb
import numpy as np
import sys

aw = pd.read_csv("aw-simulated-returns.csv")
aw = aw[np.isfinite(aw['Simulated Returns'])]

start = aw['Date'].iloc[0]
end = datetime.datetime.now()

df = web.DataReader("SPY", "yahoo", start, end)
df.to_csv("spy.csv")
aw.to_csv("aw.csv")
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 15:49:15 2018

@author: daniel
"""

from QuantLib import *
import matplotlib.pyplot as plt
import seaborn as sns
import utils
import pandas as pd

sns.set()

Settings.instance().evaluationDate = Date(3, October, 2014)

helpers = [SwapRateHelper(QuoteHandle(SimpleQuote(rate/100.0)),
                          Period(*tenor), 
                          TARGET(),
                          Annual, 
                          Unadjusted,
                          Thirty360(),
                          Euribor6M())
            for tenor, rate in [((2,Years), 1),((3,Years), 2),
                                ((5,Years), 3),((10,Years), 4),
                                ((15,Years), 5)] ]



curve1 = PiecewiseFlatForward(0, TARGET(), helpers, Actual360())

today = curve1.referenceDate()
end = today + Period(15,Years)
dates = [Date(serial) for serial in range(today.serialNumber(), end.serialNumber()+1) ]
rates_c = [curve1.forwardRate(d, TARGET().advance(d,1,Days), Actual360(), Simple).rate()
                     for d in dates ]

dates = [float(x - today)/360 for x in dates]
#dates = [pd.datetime(x.year(), x.month(), x.dayOfMonth()) for x in dates]

forward_rates = pd.DataFrame(rates_c, index = dates)

plt.plot(forward_rates)
plt.tight_layout()

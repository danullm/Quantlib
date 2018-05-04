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
plt.style.use('seaborn-whitegrid')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------


Settings.instance().evaluationDate = Date(3, October, 2014)


# Create curve from market observations --------------------------------------
#-----------------------------------------------------------------------------


helpers = [SwapRateHelper(QuoteHandle(SimpleQuote(rate/100.0)),
                          Period(*tenor), 
                          TARGET(),
                          Annual, 
                          Unadjusted,
                          Thirty360(),
                          Euribor6M())
            for tenor, rate in [((2,Years), 0.201),((3,Years), 0.258),
                                ((5,Years), .464),((10,Years), 1.151),
                                ((15,Years), 1.588)] ]

curve1 = PiecewiseFlatForward(0, TARGET(), helpers, Actual360())


# Create curve from direct input ---------------------------------------------
#----------------------------------------------------------------------------- 


dates, rates = zip(*curve1.nodes())
curve2 = ForwardCurve(dates, rates, Actual360())


# look at the different curve outputs ----------------------------------------
#-----------------------------------------------------------------------------

# def dates
today = curve1.referenceDate()
end = today + Period(15,Years)
dates = [Date(serial) for serial in range(today.serialNumber(), end.serialNumber()+1) ]


# get rates from curve object
f_rates = [curve1.forwardRate(d, TARGET().advance(d,1,Days), Actual360(), Simple).rate()
                     for d in dates ]
z_rates = [curve1.zeroRate(d, Actual360(), Simple).rate() for d in dates]
y_rates = [curve1.zeroRate(d, Actual360(), Continuous).rate() for d in dates]



# convert to plotable dates
dates = [float(x - today)/360 for x in dates]
#dates = [pd.datetime(x.year(), x.month(), x.dayOfMonth()) for x in dates]


# create dataframes
forward_rates = pd.DataFrame(f_rates, index = dates)
zero_rates = pd.DataFrame(z_rates, index = dates)
yield_rates = pd.DataFrame(y_rates, index = dates)


# plot

fig, axs = plt.subplots(2,1, sharex = True)

axs[0].plot(forward_rates, label = 'F(t,t+1)')
axs[0].plot(zero_rates, label = 'L(t)')
axs[0].plot(yield_rates, label = 'Y(t)')
axs[0].set_title("Flat Forward Curve")

# Create smooth curve from market data ---------------------------------------
#----------------------------------------------------------------------------- 

y_curve = PiecewiseLogCubicDiscount(0, TARGET(), helpers, Actual360())

today = y_curve.referenceDate()
end = today + Period(15,Years)
dates = [Date(serial) for serial in range(today.serialNumber(), end.serialNumber()+1) ]


# get rates from curve object
f_rates = [y_curve.forwardRate(d, TARGET().advance(d,1,Days), Actual360(), Simple).rate()
                     for d in dates ]
z_rates = [y_curve.zeroRate(d, Actual360(), Simple).rate() for d in dates]
y_rates = [y_curve.zeroRate(d, Actual360(), Continuous).rate() for d in dates]


# convert to plotable dates
dates = [float(x - today)/360 for x in dates]
#dates = [pd.datetime(x.year(), x.month(), x.dayOfMonth()) for x in dates]


# create dataframes
forward_rates = pd.DataFrame(f_rates, index = dates)
zero_rates = pd.DataFrame(z_rates, index = dates)
yield_rates = pd.DataFrame(y_rates, index = dates)


# plot
axs[1].plot(forward_rates, label = 'F(t,t+1)')
axs[1].plot(zero_rates, label = 'L(t)')
axs[1].plot(yield_rates, label = 'Y(t)')
axs[1].set_title("Splines Forward Curve")

[ax.legend(loc = 0, frameon=True, shadow = True) for ax in axs]
[ax.set_xlabel('Tenor / Years') for ax in axs]
[ax.set_ylabel('Rate') for ax in axs]
plt.tight_layout()
plt.show()

# Moving the evaluation date -------------------------------------------------
#-----------------------------------------------------------------------------

Settings.instance().evaluationDate = Date(19, September, 2015)

print curve1.referenceDate(), 'to', curve1.maxDate()
print curve2.referenceDate(), 'to', curve2.maxDate()

print curve1.zeroRate(5.0, Continuous)
print curve2.zeroRate(5.0, Continuous)

# def dates
today = curve1.referenceDate()
end = today + Period(10,Years)
dates = [Date(serial) for serial in range(today.serialNumber(), end.serialNumber()+1) ]

# get rates from curve object
y_rates_1 = [curve1.zeroRate(t, Actual360(), Continuous).rate() for t in dates]
y_rates_2 = [curve2.zeroRate(t, Actual360(), Continuous).rate() for t in dates]

dates = [float(x - today)/360 for x in dates]

#plt.plot(dates, y_rates_1, label = 'relative Input')
#plt.plot(dates, y_rates_2, label = 'absolue Input')
#plt.tight_layout()
#plt.legend()




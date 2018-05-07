#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 11:43:49 2018

@author: daniel
"""

import numpy as np
from QuantLib import * 
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
plt.style.use('seaborn-whitegrid')


#------------------------------------------------------------------------------

today = Date(11, December, 2012)
Settings.instance().evaluationDate = today

#------------------------------------------------------------------------------



eonia = Eonia()


'''
The first three instruments are three 1-day deposit that give us discounting between today and the
day after spot. They are modeled by three instances of the DepositRateHelper class with a tenor
of 1 day and a number of fixing days going from 0 (for the deposit starting today) to 2 (for the deposit
starting on the spot date).
'''
depos = [(0.04, 0), (0.04, 1), (0.04, 2)]

helpers = [ DepositRateHelper(QuoteHandle(SimpleQuote(rate/100)), Period(1,Days), fixingDays, TARGET(), Following, False, Actual360())
            for rate, fixingDays in depos ]

'''
Then, we have a series of OIS quotes for the first month. They are modeled by instances of the
OISRateHelper class with varying tenors. They also require an instance of the Eonia class, which
doesn’t need a forecast curve and can be shared between the helpers.
'''
ois_quotes1 = [(0.070, (1,Weeks)), (0.069, (2,Weeks)), (0.078, (3,Weeks)), (0.074, (1,Months))]

helpers += [ OISRateHelper(2, Period(*tenor), QuoteHandle(SimpleQuote(rate/100)), eonia) 
            for rate, tenor in ois_quotes1 ]

'''
Next, five OIS forwards on ECB dates. For these, we need to instantiate the DatedOISRateHelper
class and specify start and end dates explicitly.
'''
ois_fras = [(0.046, Date(16,January,2013), Date(13,February,2013)), (0.016, Date(13,February,2013), Date(13,March,2013)),
            (-0.007, Date(13,March,2013), Date(10,April,2013)), (-0.013, Date(10,April,2013), Date(8,May,2013)),
            (-0.014, Date(8,May,2013), Date(12,June,2013)) ]

helpers += [ DatedOISRateHelper(start_date, end_date, QuoteHandle(SimpleQuote(rate/100)), eonia) 
            for rate, start_date, end_date in ois_fras ]

'''
Finally, we add OIS quotes up to 30 years.
'''
ois_quotes2 = [(0.002, (15,Months)), (0.008, (18,Months)), (0.021, (21,Months)), (0.036, (2,Years)), 
              (0.127, (3,Years)), (0.274, (4,Years)), (0.456, (5,Years)), (0.647, (6,Years)), 
              (0.827, (7,Years)), (0.996, (8,Years)), (1.147, (9,Years)), (1.280, (10,Years)),
              (1.404, (11,Years)), (1.516, (12,Years)), (1.764, (15,Years)), (1.939, (20,Years)),
              (2.003, (25,Years)), (2.038, (30,Years))]

helpers += [ OISRateHelper(2, Period(*tenor), QuoteHandle(SimpleQuote(rate/100)), eonia) 
            for rate, tenor in ois_quotes2 ]

'''
The curve is an instance of PiecewiseLogCubicDiscount (corresponding to the PiecewiseYield-
Curve<Discount,LogCubic> class in C++; I won’t repeat the argument for this choice made in
section 4.5 of the paper). We let the reference date of the curve move with the global evaluation
date, by specifying it as 0 days after the latter on the TARGET calendar. The day counter chosen is
not of much consequence, as it is only used internally to convert dates into times. Also, we enable
extrapolation beyond the maturity of the last helper; that is mostly for convenience as we retrieve
rates to plot the curve near its far end.
'''

eonia_curve = PiecewiseLogCubicDiscount(0, TARGET(), helpers, Actual360())

eonia_curve.enableExtrapolation()

'''
--------------------------- Turn-of-year jumps ------------------------------
'''

eonia_curve_ff = PiecewiseFlatForward(0, TARGET(), helpers, Actual360())

today = eonia_curve.referenceDate()
end = today + Period(1,Years)
dates = [Date(serial) for serial in range(today.serialNumber(), end.serialNumber()+1) ]


# get rates from curve object
f_rates_spline = [eonia_curve.forwardRate(d, TARGET().advance(d,1,Days), Actual360(), Simple).rate()
                     for d in dates ]

f_rates_flat = [eonia_curve_ff.forwardRate(d, TARGET().advance(d,1,Days), Actual360(), Simple).rate()
                     for d in dates ]

dates_plot = [float(x - today)/360 for x in dates]


plt.figure()
plt.plot(dates_plot, f_rates_spline)
plt.plot(dates_plot, f_rates_flat)
plt.show()

'''
As we see, the forward ending at the beginning of January 2013 is out of line. In order to estimate
the jump, we need to estimate a “clean” forward that doesn’t include it.
'''

nodes = list(eonia_curve_ff.nodes())
nodes[6] = (nodes[6][0], (nodes[5][1]+nodes[7][1])/2.0)

temp_dates, temp_rates = zip(*nodes)
temp_curve = ForwardCurve(temp_dates, temp_rates, eonia_curve_ff.dayCounter())

temp_rates = [ temp_curve.forwardRate(d, TARGET().advance(d,1,Days), Actual360(), Simple).rate() 
                for d in dates ]

plt.figure()
plt.plot(dates_plot, f_rates_flat)
plt.plot(dates_plot, temp_rates)
plt.show()





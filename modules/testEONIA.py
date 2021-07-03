import math
import utils
import matplotlib.pyplot as plt

import QuantLib as ql

today = ql.Date(11, ql.December, 2012)
ql.Settings.instance().evaluationDate = today

helpers = [
    ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate/100)),
                         ql.Period(1,ql.Days), fixingDays,
                         ql.TARGET(), ql.Following,
                         False, ql.Actual360())
    for rate, fixingDays in [(0.04, 0), (0.04, 1), (0.04, 2)]
]
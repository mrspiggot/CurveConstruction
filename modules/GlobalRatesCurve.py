import pandas as pd
import QuantLib as ql
from datetime import date


class GlobalRatesCurve:
    def __init__(self, currency, type, tenor):
        self.currency = currency #Currency of underlying rate.; E.g. USD, GBP, EUR
        self.tenor = tenor #Term of rate; E.g. O/N, 3M, 6M
        self.type = type #Type of curve: E.g. OIS (Discount) or LIBOR (Forecast)
        self.depo_quotes = {}
        self.ois_quotes = {}
        self.swap_quotes = {}


    def build_OIS_Curve(self):
        today = date.today()
        ref_date = ql.Date(today.day, today.month, today.year)
        ql.Settings.instance().evaluationDate = ref_date

        helpers = [
            ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate / 100)),
                                 ql.Period(1, ql.Days), fixingDays,
                                 ql.TARGET(), ql.Following,
                                 False, ql.Actual360())
            for rate, fixingDays in [(self.depo_quotes['O/N depo'], 0),
                                     (self.depo_quotes['T/N depo'], 1),
                                     (self.depo_quotes['S/N depo'], 2),
                                     (self.depo_quotes['1 wk depo'], 7),
                                     (self.depo_quotes['1 Mth depo'], 30)]

        ]

        if self.currency == "USD":
            ois = ql.FedFunds()
        elif self.currency == "EUR":
            ois = ql.Eonia()
        elif self.currency == "GBP":
            ois = ql.Sonia()
        else:
            print("Currency not supported")
            return -1


        helpers += [
            ql.OISRateHelper(2, ql.Period(*tenor),
                             ql.QuoteHandle(ql.SimpleQuote(rate / 100)), ois)
            for rate, tenor in [(self.ois_quotes['3 month OIS'], (3, ql.Months)),
                                (self.ois_quotes['6 month OIS'], (6, ql.Months)),
                                (self.ois_quotes['1 year OIS'], (12, ql.Months)),
                                (self.ois_quotes['2 year OIS'], (2, ql.Years)),
                                (self.ois_quotes['3 year OIS'], (3, ql.Years)),
                                (self.ois_quotes['5 year OIS'], (5, ql.Years)),
                                (self.ois_quotes['10 year OIS'], (10, ql.Years)),
                                (self.ois_quotes['30 year OIS'], (30, ql.Years))]
        ]

        ois_curve_c = ql.PiecewiseLogCubicDiscount(0, ql.TARGET(),
                                                     helpers, ql.Actual365Fixed())
        ois_curve_c.enableExtrapolation()

        return ois_curve_c

    def get_depo_instruments(self):
        if self.currency == "USD":
            url = "https://www.global-rates.com/en/interest-rates/libor/american-dollar/american-dollar.aspx"
        elif self.currency == "EUR":
            url = "https://www.global-rates.com/en/interest-rates/libor/european-euro/euro.aspx"
        elif self.currency == "GBP":
            url = "https://www.global-rates.com/en/interest-rates/libor/british-pound-sterling/british-pound-sterling.aspx"
        else:
            print("Currency not supported")
            return -1

        dfs = pd.read_html(url)
        self.depo_quotes['O/N depo'] = float(dfs[9].iloc[1,1].strip('\xa0%'))
        self.depo_quotes['T/N depo'] = float(dfs[9].iloc[1,1].strip('\xa0%'))
        self.depo_quotes['S/N depo'] = float(dfs[9].iloc[1,1].strip('\xa0%'))
        self.depo_quotes['1 wk depo'] = float(dfs[9].iloc[2,1].strip('\xa0%'))
        self.depo_quotes['1 Mth depo'] = float(dfs[9].iloc[4, 1].strip('\xa0%'))
        self.depo_quotes['2 Mth depo'] = float(dfs[9].iloc[5, 1].strip('\xa0%'))
        self.depo_quotes['3 Mth depo'] = float(dfs[9].iloc[6, 1].strip('\xa0%'))
        self.depo_quotes['6 Mth depo'] = float(dfs[9].iloc[9, 1].strip('\xa0%'))
        self.depo_quotes['12 Mth depo'] = float(dfs[9].iloc[15, 1].strip('\xa0%'))

    def get_OIS_instruments(self):
        if self.currency == "USD":
            DF_INDEX = 1
        elif self.currency == "EUR":
            DF_INDEX = 3
        elif self.currency == "GBP":
            DF_INDEX = 7

        else:
            print("Currency not supported")
            return -1

        dfs = pd.read_html("https://www.lch.com/services/swapclear/essentials/settlement-prices")
        for i in range(0,8):
            self.ois_quotes[dfs[DF_INDEX].iloc[i,0] + ' OIS'] = dfs[DF_INDEX].iloc[i,1]

    def get_Swap_instruments(self):
        if self.currency == "USD":
            DF_INDEX = 0
        elif self.currency == "EUR":
            DF_INDEX = 2
        elif self.currency == "GBP":
            DF_INDEX = 6

        if self.tenor == "1M":
            COL_INDEX = 1
        elif self.tenor == "3M":
            COL_INDEX = 2
        elif self.tenor == "6M":
            COL_INDEX = 3

        else:
            print("Currency not supported")
            return -1

        dfs = pd.read_html("https://www.lch.com/services/swapclear/essentials/settlement-prices")
        for i in range(0,5):
            self.swap_quotes[dfs[DF_INDEX].iloc[i,0] + ' ' + self.tenor + ' Libor'] = dfs[DF_INDEX].iloc[i,COL_INDEX]


    def build_LIBOR_curve(self, ois_curve):
        today = date.today()
        ref_date = ql.Date(today.day, today.month, today.year)
        ql.Settings.instance().evaluationDate = ref_date

        helpers = [
            ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate / 100)),
                                 ql.Period(1, ql.Days), fixingDays,
                                 ql.TARGET(), ql.Following,
                                 False, ql.Actual360())
            for rate, fixingDays in [(self.depo_quotes['O/N depo'], 0),
                                     (self.depo_quotes['T/N depo'], 1),
                                     (self.depo_quotes['S/N depo'], 2),
                                     (self.depo_quotes['1 wk depo'], 7),
                                     (self.depo_quotes['1 Mth depo'], 30),
                                     # (self.depo_quotes['2 Mth depo'], 60),
                                     # (self.depo_quotes['3 Mth depo'], 90),
                                     # (self.depo_quotes['6 Mth depo'], 180),
                                     # (self.depo_quotes['12 Mth depo'], 365)
                                     ]

        ]
        discount_curve = ql.RelinkableYieldTermStructureHandle()
        discount_curve.linkTo(ois_curve)
        euribor6m = ql.Euribor6M()

        helpers += [
            ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate / 100)),
                              ql.Period(tenor, ql.Years), ql.TARGET(),
                              ql.Annual, ql.Unadjusted,
                              ql.Thirty360(ql.Thirty360.BondBasis),
                              euribor6m, ql.QuoteHandle(), ql.Period(0, ql.Days),
                              discount_curve)
            for rate, tenor in [(self.swap_quotes['2 year ' + self.tenor + ' Libor'], 2),
                                (self.swap_quotes['3 year ' + self.tenor + ' Libor'], 3),
                                (self.swap_quotes['5 year ' + self.tenor + ' Libor'], 5),
                                (self.swap_quotes['10 year ' + self.tenor + ' Libor'], 10),
                                (self.swap_quotes['30 year ' + self.tenor + ' Libor'], 30)
                                ]
        ]


        libor_curve = ql.PiecewiseLogCubicDiscount(2, ql.TARGET(), helpers,
                                                       ql.Actual365Fixed())
        libor_curve.enableExtrapolation()

        return libor_curve

    def print_quotes(self):
        print("Depo")
        for instrument, rate in self.depo_quotes.items():
            print("Instrument: ", instrument, "Rate: ", rate)

        print("OIS")
        for instrument, rate in self.ois_quotes.items():
            print("Instrument: ", instrument, "Rate: ", rate)

        print("Swap")
        for instrument, rate in self.swap_quotes.items():
            print("Instrument: ", instrument, "Rate: ", rate)

# c1 = GlobalRatesCurve("GBP", "OIS", "O/N")
# c2 = GlobalRatesCurve("GBP", "LIBOR", "1M")
# c1.get_depo_instruments()
# c1.get_OIS_instruments()
# c1.print_quotes()
# zeros = c1.build_OIS_Curve()
# c2.get_depo_instruments()
# c2.get_Swap_instruments()
# libor = c2.build_LIBOR_curve(zeros)
#
# today = zeros.referenceDate()
# end = today + ql.Period(20,ql.Years)
# dates = [ ql.Date(serial) for serial in range(today.serialNumber(),
#                                               end.serialNumber()+1) ]
# rates_c = [ zeros.forwardRate(d, ql.TARGET().advance(d,1,ql.Days),
#                                       ql.Actual360(), ql.Simple).rate()
#             for d in dates ]
#
# spot = libor.referenceDate()
# dates = [ spot+ql.Period(i,ql.Months) for i in range(0, 60*12+1) ]
# rates = [ libor.forwardRate(d, ql.Euribor6M().maturityDate(d),
#                                       ql.Actual360(), ql.Simple).rate()
#           for d in dates ]
#
#
# print(dates)
# print(rates_c)
# print(rates)
#
# c1.print_quotes()
# c2.print_quotes()

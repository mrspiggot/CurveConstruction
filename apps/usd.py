from modules.GlobalRatesCurve import GlobalRatesCurve
import dash_html_components as html
import dash_core_components as dcc
from app import app
from dash.dependencies import Input, Output
import datetime
import pandas as pd
import QuantLib as ql
import plotly.express as px


def ql_to_datetime(d):
    return datetime.datetime(d.year(), d.month(), d.dayOfMonth())


layout = html.Div([
    dcc.Dropdown(
        options=[
            {'label': 'OIS', 'value': 'OIS O/N'},
            {'label': '1M Libor', 'value': 'LIBOR 1M'},
            {'label': '3M Libor', 'value': 'LIBOR 3M'},
            {'label': '6M Libor', 'value': 'LIBOR 6M'}
        ],
        value=['OIS O/N', 'LIBOR 6M'],
        multi=True,
        id="curve-dd"
    ),
    dcc.Loading(
        html.Div(id='zero', children=[]),fullscreen=True, type='circle'
        ),
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='OIS', value='tab-ois'),
        dcc.Tab(label='1M Libor', value='tab-1M'),
        dcc.Tab(label='3M Libor', value='tab-3M'),
        dcc.Tab(label='6M Libor', value='tab-6M'),
    ]),
    html.Div(id='tabs-example-content')
])

@app.callback(Output('zero', 'children'),
              [Input('curve-dd', 'value')], prevent_initial_call=True)
#@cache.memoize(timeout=20)
def display_zero_curve(dd_value):
    zeros = []
    rates = []
    for curve in dd_value:
        z = GlobalRatesCurve("USD", curve.split(' ')[0], curve.split(' ')[1])
        z.get_depo_instruments()
        if curve.split(' ')[0]=="OIS":
            z.get_OIS_instruments()
            ois = z.build_OIS_Curve()
            today = ois.referenceDate()
            end = today + ql.Period(60, ql.Years)
            # dates_o = [ql.Date(serial) for serial in range(today.serialNumber(),
            #                                                end.serialNumber() + 1)]
            dates_o = [today + ql.Period(i, ql.Months) for i in range(0, 60 * 12 + 1)]
            rates_c = [ois.forwardRate(d, ql.TARGET().advance(d, 1, ql.Days),
                                         ql.Actual360(), ql.Simple).rate()
                       for d in dates_o]
            rates.append(rates_c)
        else:
            z.get_Swap_instruments()
            libor = z.build_LIBOR_curve(ois)
            spot = libor.referenceDate()
            dates_l = [spot + ql.Period(i, ql.Months) for i in range(0, 60 * 12 + 1)]
            rates_l = [libor.forwardRate(d, ql.Euribor6M().maturityDate(d),
                                         ql.Actual360(), ql.Simple).rate()
                       for d in dates_l]
            rates.append(rates_l)

        zeros.append(z)

    d_list = []
    for date in dates_o:
        d = ql_to_datetime(date)
        d_list.append(d)

    points = []
    points.append(d_list)
    for vector in rates:
        points.append(vector)

    flip = list(map(list, zip(*points)))
    df = pd.DataFrame(flip)

    trace = dd_value
    dd_value.insert(0, "Date")
    df.columns = dd_value

    chart = dcc.Graph(figure=px.line(df, x='Date', y=trace))

    return chart


from pathlib import Path
from app import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from modules.GlobalRatesCurve import GlobalRatesCurve
from PIL import Image

cwd = Path.cwd()


img = Image.open(cwd.joinpath('assets/Color logo - no background.png'))

navbar = dbc.NavbarSimple(
    children=[
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=img, height="90px")),
     #                   dbc.Col(dbc.NavbarBrand("Lucidate", className="ml-2", href="/home")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/",
            ),
        dbc.NavItem(dbc.NavLink("Swap Portfolio", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("USD Curves", header=True, href="usd"),
                dbc.DropdownMenuItem("EUR Curves", href="eur"),
                dbc.DropdownMenuItem("GBP Curves", href="gbp"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Lucidate",
    brand_href="/",
    color="#444f4a",
    dark=True,
)

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

def serve_layout():
    return html.Div([
    dcc.Location(id='page-url'),
    html.Div([
        navbar,
    ]),
    html.Div(id='page-content', children=[]),
],
style=CONTENT_STYLE)

app.layout = serve_layout


@app.callback(Output('page-content', 'children'),
              [Input('page-url', 'pathname')], prevent_initial_call=True)
#@cache.memoize(timeout=20)
def display_page(pathname):
    if pathname == '/usd':
        return usd.layout

if __name__ == '__main__':
    app.run_server(debug=True)
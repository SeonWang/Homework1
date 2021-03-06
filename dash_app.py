import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from os import listdir, remove
import pickle
from time import sleep

from helper_functions import * # this statement imports all functions from your helper_functions file!

# Run your helper function to clear out any io files left over from old runs
check_for_and_del_io_files()

# create options in Dropdowns
catalog_df = pd.read_csv('pairs_catalog.csv')
options = [{'label': x, 'value': y} for x in catalog_df['label'] for y in catalog_df['value'] if x == y]

# Make a Dash app!
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Define the layout.
app.layout = html.Div([
    # Section1title
    html.H1("Section 1: Fetch & Display exchange rate historical data"),

    # Currency pair text input, within its own div.
    html.Div(['Select a currency pair', dcc.Dropdown(id='section1-dropdown', options=options,value='')]),
    html.Div(id='output-div', children='This is a default value.'),

    # Line break
    html.Br(),

    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div([
        # Candlestick graph goes here:
        dcc.Graph(id='candlestick-graph')
    ]),

    # Another line break
    html.Br(),

    # Section2 title
    html.H1("Section 2: Make a Trade"),
    # Div to confirm what trade was made
    html.Div(id='trade-confirm', children='enter a trade'),
    # Radio items to select buy or sell
    html.Div(dcc.RadioItems(
            id='buy-or-sell',
            options=[
                {'label': 'BUY', 'value': 'BUY'},
                {'label': 'SELL', 'value': 'SELL'}
            ],
            value='BUY',
        )),
    # Trade information
    html.Div([
        dcc.Dropdown(id='section2-dropdown', options=options, value=''),
        dcc.Input(id='trade-amount', value='', type='number', min=0),
        html.Button('Trade', id='trade-button', n_clicks=0)
    ]
    )
])

# Callback for what to show in figure
@app.callback(
    [Output('output-div', 'children'),
     Output('candlestick-graph', 'figure')],
    [Input('section1-dropdown', 'value')]
)
def update_candlestick_graph(value):

    # Now we're going to save the value of currency-input as a text file.
    with open("currency_pair.txt", "w") as f:
        f.write(value)

    # Wait until ibkr_app runs the query and saves the historical prices csv
    while True:
        if 'currency_pair_history.csv' in listdir():
            sleep(0.5)
            break
        else:
            continue
    # Read in the historical prices
    df = pd.read_csv('currency_pair_history.csv')

    # Remove the file 'currency_pair_history.csv'
    remove('currency_pair_history.csv')

    # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        ],
        layout=dict(title=value, xaxis=dict(type='date'))
    )
    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
    return ('Submitted query for ' + value), fig

# Callback for what to trade
@app.callback(
    Output('trade-confirm', 'children'),
    [Input('trade-button', 'n_clicks'),
     State('buy-or-sell', 'value'),
     State('section2-dropdown', 'value'),
     State('trade-amount', 'value')
     ], prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt): # Still don't use n_clicks, but we need the dependency
    # Make the message that we want to send back to trade-output
    msg = action + ' ' + str(trade_amt) + ' ' + trade_currency

    # Make our trade_order object -- a DICTIONARY.
    trade_order = {
        "action": action,
        "trade_currency": trade_currency,
        "trade_amt": trade_amt
    }

    # Dump trade_order as a pickle object to a file connection opened with write-in-binary ("wb") permission:
    pickle.dump(trade_order, open("trade_order.p", "wb"))

    # Return the message, which goes to the trade-output div's "children" attribute.
    return msg

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)

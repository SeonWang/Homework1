# make your imports
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from os import listdir, remove
from helper_functions import *
import pickle

#check_for_and_del_io_files()

# create an app object of class 'Dash'
app = dash.Dash(__name__)

# Define the layout of the dash page.
app.layout = html.Div([
    html.H1('Section1'),
    html.Div(dcc.Input(id = 'currency-pair', value="", type = 'text'), style={'display': 'inline-block'}),
    html.Button('Submit', id = 'submit-button', n_clicks = 0),
    html.Div(id='output-div', children='This is a default value.'),
    html.Div([
        # Candlestick graph goes here:
        dcc.Graph(id='candlestick-graph')
    ]),
    html.H1('Section2'),
    html.Div(id='trade-confirm', children='enter a trade'),
    html.Div(dcc.RadioItems(
        id='buy_or_sell',
        options=[
            {'label': 'BUY', 'value': 'BUY'},
            {'label': 'SELL', 'value': 'SELL'}
        ],
        value='BUY',
    )),
    html.Div([
        dcc.Input(id='currency-pair-traded', value='', type='text'),
        dcc.Input(id='trade-amount', value='', type='number', min=0),
        html.Button('Trade', id='trade-button', n_clicks=0)
        ]
    )
])

@app.callback(
    [Output('output-div', 'children'),
     Output('candlestick-graph', 'figure')],
    [Input('submit-button', 'n_clicks'),
    State('currency-pair', 'value')]
)
def update_candlestick_graph(n_clicks, value):
    # 创建文件pair文件
    with open("currency_pair.txt", "w") as f:
        f.write(value)

    # 检测
    while True:
        if 'currency_pair_history.csv' in listdir():
            break

    # 1) Read in the candlestick data from Plotly's example data sets on GitHub:
    df = pd.read_csv('currency_pair_history.csv')

    # 2) Make the candlestick figure
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
    return ('Submitted query for ' + value), fig

@app.callback(
    Output('trade-confirm', 'children'),
    [Input('trade-button', 'n_clicks'),
     State('buy_or_sell', 'value'),
     State('currency-pair-traded', 'value'),
     State('trade-amount', 'value')
     ], prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt):
    trade_order = {
        "action": action,
        "trade_currency": trade_currency,
        "trade_amt": trade_amt
    }
    pickle.dump(trade_order, open("trade_order.p", "wb"))
    return action + ' ' + str(trade_amt) + ' ' + trade_currency

if __name__ == '__main__':
    app.run_server(debug=True)

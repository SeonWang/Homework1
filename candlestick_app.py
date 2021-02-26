# Fetches and displays a basic candlestick app.

# Example for making a basic candlestick plot, changing an attribute ("Title"), and displaying in Dash
import dash
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output

# 1) Read in the candlestick data from Plotly's example data sets on GitHub:
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

# 2) Make the candlestick figure
fig = go.Figure(
    data=[
        go.Candlestick(
            x=df['Date'],
            open=df['AAPL.Open'],
            high=df['AAPL.High'],
            low=df['AAPL.Low'],
            close=df['AAPL.Close']
        )
    ],
    layout=dict(title='Apple OHLC')
)

# 3) Create a Dash app
app = dash.Dash(__name__)

# 4) Define a very simple layout -- just a plot inside a div. No inputs or outputs because the figure doesn't change.
app.layout = html.Div([dcc.Graph(id='candlestick-graph', figure=fig)])

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)

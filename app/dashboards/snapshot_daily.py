import dash
import pandas as pd
import plotly.express as px
import os, sys

from dash import dcc
from dash import html

# Following lines are for assigning the parent directory dynamically.
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
pp_dir_path = os.path.abspath(os.path.join(parent_dir_path, os.pardir))
sys.path += [parent_dir_path, pp_dir_path]

from datasets.CoinGecko import CoinGecko

# Get data from CoinGecko
cg = CoinGecko()
data = cg.get_marketcap_dataframe(topn=100)

# Initialize the Dash app
app = dash.Dash(__name__)

# Apply custom styles to the app
app.css.append_css({
    'external_url': 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/slate/bootstrap.min.css'
})

# Create the treemap chart
def create_treemap_chart():
    fig = px.treemap(data, path=['symbol'], values='market_cap')
    fig.update_traces(textinfo='label+percent entry')
    fig.update_layout(margin=dict(t=40, b=40, r=40, l=40))
    return dcc.Graph(figure=fig, id='treemap-chart')

# Create the bar chart for total_volume
def create_bar_chart():
    fig = px.bar(data, x='symbol', y='total_volume', color='symbol', title='Total Volume')
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title='Symbol')
    fig.update_yaxes(title='Total Volume')
    fig.update_layout(margin=dict(t=40, b=40, r=40, l=40))
    return dcc.Graph(figure=fig, id='bar-chart')

# Define the layout of the app
app.layout = html.Div(
    style={'backgroundColor': '#f8f9fa'},
    children=[
        html.H1("Market Data Dashboard", style={'textAlign': 'center', 'marginTop': '20px'}),
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='six columns',
                    children=[
                        html.H3("Treemap Chart", style={'textAlign': 'center'}),
                        create_treemap_chart()
                    ],
                ),
                html.Div(
                    className='six columns',
                    children=[
                        html.H3("Total Volume Bar Chart", style={'textAlign': 'center'}),
                        create_bar_chart()
                    ],
                ),
            ],
            style={'marginTop': '40px'}
        ),
    ]
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

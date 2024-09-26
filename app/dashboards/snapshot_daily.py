import os, sys
import dash
from dash import html
import dash_bootstrap_components as dbc

from app.dashboards.utils import draw_figure, draw_text
from app.dashboards.visualizations.treemap import create_treemap_chart
from app.dashboards.visualizations.bar import create_bar_chart

# Following lines are for assigning the parent directory dynamically.
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
pp_dir_path = os.path.abspath(os.path.join(parent_dir_path, os.pardir))
sys.path += [parent_dir_path, pp_dir_path]

from datasets.CoinGecko import CoinGecko

# Get data from CoinGecko
cg = CoinGecko()
data = cg.get_marketcap_df(topn=100)

# Initialize the Dash app
external_stylesheets = [
    dbc.themes.SLATE
    #dbc.themes.CYBORG,
    #'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/slate/bootstrap.min.css',
]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets
)

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    draw_text(
                        "Market Data Dashboard",
                        level=1,
                        additional_style={'marginTop': '20px'}
                    )
                ], width=12),
            ], align='center'), 
            html.Br(),
            dbc.Row([   
                dbc.Col([
                    draw_text("Market Capitalization", level=3)
                ], width=12),
            ], align='center'), 
            dbc.Row([   
                dbc.Col([
                    draw_figure(create_treemap_chart(
                        data,
                        path=['symbol'],
                        values='market_cap',
                        return_fig=True,
                    ))
                ], width=12),
            ], align='center'),
            html.Br(),
            dbc.Row([   
                dbc.Col([
                    draw_text("Total Volume", level=3)
                ], width=12),
            ], align='center'), 
            dbc.Row([   
                dbc.Col([
                    draw_figure(
                        create_bar_chart(
                            data,
                            x='symbol',
                            y='total_volume',
                            color='symbol',
                            title='Total Volume',
                            x_axe_title='Symbol',
                            y_axe_title='Total Volume',
                            return_fig=True,
                    ))
                ], width=12),
            ], align='center'),
        ]), color = 'dark'
    )
])

# Run app and display result inline in the notebook
app.run_server()
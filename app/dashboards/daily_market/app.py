# dashboards/daily_market/app.py

import dash_bootstrap_components as dbc
import pandera as pa
import plotly.express as px
import sys, os

from dash import Dash, html, dcc, Input, Output
from dash.dash_table import DataTable
from pandera.typing import DataFrame
from plotly.graph_objs import Layout
from typing import List, Optional


#Following lines are for assigning parent directory dynamically.
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
pp_dir_path = os.path.abspath(os.path.join(parent_dir_path, os.pardir))
sys.path += [parent_dir_path, pp_dir_path]


from clients.CoinGeckoClient import CoinGeckoClient
from schemas.DailyMarketSchema import DailyMarketSchema


###################
""" Script Parameters
"""
# Set to None to get information for all assets
SUBSET_ID = "random-10"
NUMBER_OF_DAYS = 30
METRICS = ["prices", "total_volumes", "market_caps"]

###################
""" Data Extraction 
"""
# Create Client
client_usd = CoinGeckoClient(SUBSET_ID, "usd")

# Get market data
df_market = client_usd.daily_market_data(NUMBER_OF_DAYS, metrics=METRICS)

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
###################
""" Dashboard functions
"""

@pa.check_types
def dashboard_daily_market(
    dataframe: DataFrame[DailyMarketSchema],
    metrics: Optional[List[str]] = None
) -> html.Div:
    """Return dashboard with Data Quality metrics on a daily_market DataFrame.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        A dataframe that is validated using schemas.DailarketSchema
    """
    bottom_table = dataframe[dataframe["dates"] == dataframe["dates"].max()]
    assets = dataframe["asset_name"].unique()

    controls = dbc.Card([
        html.Div([
            dbc.Label("Select a metric:"),
            dcc.Dropdown(
                id="filter-metric",
                options=metrics,
                clearable=False,
                value="prices"
            )
        ]),
        html.Div([
            dbc.Label("Select an asset:"),
            dcc.Dropdown(
                id="filter-asset",
                options=assets,
                clearable=False,
                value=assets[0]
            )
        ])
    ], body=True)

    return dbc.Container([
        html.H1("Data Quality Report"),
        html.Hr(),
        dbc.Row([
            dbc.Col(controls, md=4),
            dbc.Col(dcc.Graph(id="metric_line_chart"), md=8)
        ], align="center"),
        html.Hr(),
        dbc.Col(dcc.Graph(id="na_figure"), md=12),
        html.Hr(),
        dbc.Col(DataTable(
            id='data_table',
            columns=[{'id': c, 'name': c} for c in dataframe.columns],
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            }
        ), md=12)
    ], fluid=True)

@app.callback(
    Output("metric_line_chart", "figure"),
    Input("filter-metric", "value"),
    Input("filter-asset", "value"))
def update_metric_line_chart(metric: str, asset: str):
    df = df_market[["dates", "asset_name", metric]]
    df = df[df["asset_name"] == asset].sort_values(by=["dates"])
    fig = px.line(
        df,
        x="dates", y=metric,
        color="asset_name",
        labels = {
            "dates": "Date",
            metric: f"{metric} ($USD)"
        },
        template="plotly_dark"
    )
    #fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)','paper_bgcolor': 'rgba(0,0,0,0)'})
    return fig

@app.callback(
    Output("na_figure", "figure"),
    Input("filter-asset", "value"))
def get_na_figure(asset: str):
    df = df_market.loc[df_market["asset_name"] == asset]
    df = df[METRICS]
    series_null_count = 100.0 * df.isnull().sum() / len(df)
    df_null_count = series_null_count.reset_index()

    fig = px.bar(
        df_null_count,
        x="index",
        y=0,
        labels={
            "index": " ",
        },
        template="plotly_dark",
        title="Percentage of Null values in the extracted data"
    )

    #fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)','paper_bgcolor': 'rgba(0,0,0,0)'})

    return fig

@app.callback(
    Output("data_table", "data"),
    Input("filter-asset", "value"))
def generate_datatable(asset: str):
    df = df_market.loc[df_market["asset_name"] == asset]
    return df.to_dict('records')


if __name__ == "__main__":
    # visit http://127.0.0.1:8888/ to visualize the report
    app.layout = dashboard_daily_market(df_market, metrics=METRICS)
    app.run_server(debug=True, port=8888)
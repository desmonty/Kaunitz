import os
import sys
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Import your strategies
from app.analytics.Top5MarketCapStrategy import Top5MarketCapStrategy
from app.analytics.Top5MarketCapStrategyRebalanced import Top5MarketCapStrategyRebalanced

# Adjust the system path to include your app directory
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
pp_dir_path = os.path.abspath(os.path.join(parent_dir_path, os.pardir))
sys.path += [parent_dir_path, pp_dir_path]


from app.datasets.CoinGecko import CoinGecko
from app import config

# Get data from CoinGecko
cg = CoinGecko()
data = cg.get_historical_df(
    quote="usd", days=365, assets_ids=config.universe[:10]
)
data["timestamp"] = pd.to_datetime(data["timestamp"]).dt.tz_localize("UTC")
data["date"] = data["timestamp"].dt.date
data["date"] = pd.to_datetime(data["date"])

# Define the cron expression for every month
rebalance_cron = "0 0 2 * *"

# Instantiate the strategies
strategy_acc = Top5MarketCapStrategy(
    data=data, rebalance_cron=rebalance_cron, investment_amount=400
)

strategy_reb = Top5MarketCapStrategyRebalanced(
    data=data, rebalance_cron=rebalance_cron, investment_amount=400
)

# Run backtests
results_acc = strategy_acc.backtest()
results_reb = strategy_reb.backtest()

# Prepare data for visualization
# Combine portfolio value histories for both strategies
portfolio_acc = results_acc['portfolio_value_history'].copy()
portfolio_acc['Strategy'] = 'Accumulation'

portfolio_reb = results_reb['portfolio_value_history'].copy()
portfolio_reb['Strategy'] = 'Rebalanced'

portfolio_history = pd.concat([portfolio_acc, portfolio_reb], ignore_index=True)

# Create line chart for portfolio values
portfolio_fig = px.line(
    portfolio_history,
    x='date',
    y='portfolio_value',
    color='Strategy',
    title='Portfolio Value Over Time',
    labels={'portfolio_value': 'Portfolio Value (USD)', 'date': 'Date'},
)

# Prepare summary statistics
summary_df = pd.DataFrame({
    'Strategy': ['Accumulation', 'Rebalanced'],
    'PnL': [results_acc['pnl'], results_reb['pnl']],
    'Transaction Costs': [results_acc['transaction_costs'], results_reb['transaction_costs']],
})

# Initialize the Dash app
external_stylesheets = [dbc.themes.SLATE]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dbc.Container([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H1("Strategy Backtest Dashboard", style={'marginTop': '20px', 'textAlign': 'center'}),
                    ], width=12),
                ], align='center'),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H3("Portfolio Value Comparison", style={'textAlign': 'center'}),
                        dcc.Graph(figure=portfolio_fig),
                    ], width=12),
                ], align='center'),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H3("Summary Statistics", style={'textAlign': 'center'}),
                        dbc.Table.from_dataframe(
                            summary_df,
                            striped=True,
                            bordered=True,
                            hover=True,
                            dark=True,
                            style={'textAlign': 'center'},
                        ),
                    ], width=12),
                ], align='center'),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H3("Trades Executed - Accumulation Strategy", style={'textAlign': 'center'}),
                        dcc.Graph(
                            figure=px.scatter(
                                pd.DataFrame(results_acc['trades']),
                                x='date',
                                y='quantity',
                                color='asset',
                                title='Trades Over Time (Accumulation)',
                                labels={'quantity': 'Quantity', 'date': 'Date'},
                            )
                        ),
                    ], width=12),
                ], align='center'),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H3("Trades Executed - Rebalanced Strategy", style={'textAlign': 'center'}),
                        dcc.Graph(
                            figure=px.scatter(
                                pd.DataFrame(results_reb['trades']),
                                x='date',
                                y='quantity',
                                color='asset',
                                title='Trades Over Time (Rebalanced)',
                                labels={'quantity': 'Quantity', 'date': 'Date'},
                            )
                        ),
                    ], width=12),
                ], align='center'),
            ]), color='dark'
        )
    ], fluid=True)
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

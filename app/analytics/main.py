import pandas as pd

from app.analytics.Top5MarketCapStrategyAccumulated import Top5MarketCapStrategyAccumulated
from app.analytics.Top5MarketCapStrategyRebalanced import Top5MarketCapStrategyRebalanced


if __name__ == "__main__":
    # Assuming `data` is your DataFrame with columns: 'date', 'asset', 'price', 'market_cap', 'volume', 'returns'
    import datetime as dt
    from app.datasets.CoinGecko import CoinGecko
    from app import config

    # Get data from CoinGecko
    cg = CoinGecko()
    data = cg.get_historical_df(
        quote="usd", days=365, until=dt.date.today(), assets_ids=config.universe[:10]
    )
    data["timestamp"] = pd.to_datetime(data["timestamp"]).dt.tz_localize("UTC")
    # Then extract date
    data["date"] = data["timestamp"].dt.date
    data["date"] = pd.to_datetime(data["date"])

    # Define the cron expression for every month
    rebalance_cron = "0 0 2 * *"

    # Instantiate the strategy
    strategy_acc = Top5MarketCapStrategyAccumulated(
        data=data, rebalance_cron=rebalance_cron, investment_amount=400
    )

    strategy_reb = Top5MarketCapStrategyRebalanced(
        data=data, rebalance_cron=rebalance_cron, investment_amount=400
    )

    # Run backtest
    results_acc = strategy_acc.backtest()
    #results_reb = strategy_reb.backtest()

    # Output results
    print("PnL:", results_acc["pnl"])
    print("Transaction Costs:", results_acc["transaction_costs"])
    print("Portfolio Value History:")
    print(results_acc["portfolio_value_history"])
    print("Trades Executed:")
    print(pd.DataFrame(results_acc["trades"]))

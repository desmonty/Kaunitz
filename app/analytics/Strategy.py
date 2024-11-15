from abc import ABC, abstractmethod
import pandas as pd
import datetime as dt
import logging
from croniter import croniter

from app.analytics.Holdings import Holdings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Strategy(ABC):
    def __init__(self, data, rebalance_cron, investment_amount):
        self.data = data.copy()
        self.rebalance_cron = rebalance_cron
        self.investment_amount = investment_amount
        self.start_date = data['date'].min()
        self.end_date = data['date'].max()
        self.rebalance_dates = self._generate_rebalance_dates()
        self.trades = []
        self.transaction_costs = 0
        self.pnl = 0
        self.portfolio_value_history = pd.DataFrame(columns=['date', 'portfolio_value'])
        self.holdings = Holdings()

    def _generate_rebalance_dates(self):
        """Generate rebalancing dates based on the cron expression."""
        cron = croniter(self.rebalance_cron, self.start_date)
        dates = []
        next_date = cron.get_next(dt.datetime)
        while next_date <= self.end_date:
            # Ensure the date exists in the data
            dates.append(next_date)
            next_date = cron.get_next(dt.datetime)
        return dates

    def backtest(self):
        """Run the backtest over the historical data."""
        for rebalance_date in self.rebalance_dates:
            self.rebalance(rebalance_date)
        # Calculate final PnL
        initial_investment = self.investment_amount * len(self.rebalance_dates)
        final_value = self.portfolio_value_history.iloc[-1]['portfolio_value']
        self.pnl = final_value - initial_investment - self.transaction_costs
        # Return results
        return {
            'pnl': self.pnl,
            'transaction_costs': self.transaction_costs,
            'portfolio_value_history': self.portfolio_value_history,
            'trades': self.trades
        }

    def rebalance(self, current_date):
        """Perform rebalancing on the specified date."""
        historical_data = self.data[self.data['date'] <= current_date]
        selected_assets = self.selection(current_date, historical_data)
        weights = self.weighting(selected_assets, current_date, historical_data)
        self.execution(current_date, weights)
        self._update_portfolio_value(current_date)


    @abstractmethod
    def selection(self, current_date, historical_data):
        """Select assets to trade."""
        pass

    @abstractmethod
    def weighting(self, selected_assets, current_date, historical_data):
        """Calculate weights for each selected asset."""
        pass

    @abstractmethod
    def execution(self, current_date, weights):
        """Execute trades based on the calculated weights."""
        pass

    def get_priced_holdings(self, date):
        holdings = self.holdings.state()
        holdings["date"] = date
        holdings_with_prices = pd.merge(
            holdings,
            self.data[['date', 'asset', 'prices']],
            on=["date", "asset"],
            how="left"
        )
        return holdings_with_prices

    def _update_portfolio_value(self, current_date):
        """Update the portfolio value."""
        holdings_with_prices = self.get_priced_holdings(current_date)
        total_value = 0
        for _, row in holdings_with_prices.iterrows():
            asset = row['asset']
            quantity = row['quantity']
            price_row = self.data[
                (self.data['date'] == current_date) & (self.data['asset'] == asset)
            ]
            if price_row.empty:
                continue
            price = price_row['prices'].values[0]
            total_value += quantity * price
        new_row = pd.DataFrame([{
            'date': current_date,
            'portfolio_value': total_value
        }])
        self.portfolio_value_history = pd.concat([self.portfolio_value_history, new_row], ignore_index=True)

import pandas as pd
from app.analytics.Strategy import Strategy


class Top5MarketCapStrategyRebalanced(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.holdings = pd.DataFrame(columns=['asset', 'quantity'])

    def selection(self, current_date, historical_data):
        """Select the top 5 assets by market capitalization."""
        current_data = historical_data[historical_data['date'] == current_date]
        top_assets = current_data.nlargest(5, 'market_caps')['asset'].tolist()
        return top_assets

    def weighting(self, selected_assets, current_date, historical_data):
        """Weight assets based on their market capitalization."""
        current_data = historical_data[
            (historical_data['date'] == current_date) &
            (historical_data['asset'].isin(selected_assets))
        ]
        total_market_cap = current_data['market_caps'].sum()
        weights = {
            row['asset']: row['market_caps'] / total_market_cap
            for _, row in current_data.iterrows()
        }
        return weights

    def get_price(self, asset, date):
        price_row = self.data[
            (self.data['date'] == date) & (self.data['asset'] == asset)
        ]
        if price_row.empty:
            return None
        return price_row['prices'].values[0]

    def execution(self, current_date, weights):
        """Execute trades based on the calculated weights, performing a classic rebalance."""
        # First, get current holdings
        if self.holdings.empty:
            # No holdings yet
            current_holdings = pd.DataFrame(columns=['asset', 'quantity', 'value'])
        else:
            # Get current prices for current holdings
            holdings_with_prices = self.holdings.copy()
            holdings_with_prices['prices'] = holdings_with_prices['asset'].apply(
                lambda asset: self.get_price(asset, current_date)
            )
            holdings_with_prices['value'] = holdings_with_prices['quantity'] * holdings_with_prices['prices']
            current_holdings = holdings_with_prices[['asset', 'quantity', 'value']]

        # Calculate total portfolio value (including new investment)
        total_portfolio_value = current_holdings['value'].sum() + self.investment_amount

        transaction_cost = 0
        trades = []

        # Sell assets that are not in new selected assets
        assets_to_sell = set(current_holdings['asset']) - set(weights.keys())
        for asset in assets_to_sell:
            # Sell all holdings
            quantity = current_holdings.loc[current_holdings['asset'] == asset, 'quantity'].values[0]
            price = self.get_price(asset, current_date)
            value = quantity * price
            trades.append({
                'date': current_date,
                'asset': asset,
                'quantity': -quantity,  # Negative quantity indicates selling
                'prices': price
            })
            # Add value to cash (already included in total_portfolio_value)
            # Assume transaction cost of 0.1%
            transaction_cost += value * 0.001

        # For assets in new selected assets, calculate desired holdings
        desired_holdings = {}
        for asset in weights.keys():
            desired_value = total_portfolio_value * weights[asset]
            price = self.get_price(asset, current_date)
            desired_quantity = desired_value / price
            desired_holdings[asset] = desired_quantity

        # Adjust holdings for assets in both current holdings and desired holdings
        for asset in desired_holdings.keys():
            price = self.get_price(asset, current_date)
            desired_quantity = desired_holdings[asset]
            current_quantity = current_holdings.loc[current_holdings['asset'] == asset, 'quantity'].values[0] if asset in current_holdings['asset'].values else 0
            delta_quantity = desired_quantity - current_quantity  # Positive: buy, Negative: sell
            if delta_quantity != 0:
                trades.append({
                    'date': current_date,
                    'asset': asset,
                    'quantity': delta_quantity,
                    'prices': price
                })
                trade_value = abs(delta_quantity * price)
                # Assume transaction cost of 0.1%
                transaction_cost += trade_value * 0.001

        # Update holdings
        # Remove sold assets
        self.holdings = self.holdings[~self.holdings['asset'].isin(assets_to_sell)]
        # Update holdings with new quantities
        for asset in desired_holdings.keys():
            desired_quantity = desired_holdings[asset]
            if asset in self.holdings['asset'].values:
                self.holdings.loc[self.holdings['asset'] == asset, 'quantity'] = desired_quantity
            else:
                self.holdings = pd.concat([self.holdings, pd.DataFrame({'asset': [asset], 'quantity': [desired_quantity]})], ignore_index=True)

        # Remove any holdings with zero quantity
        self.holdings = self.holdings[self.holdings['quantity'] != 0]

        # Record trades
        self.trades.extend(trades)

        # Update transaction costs
        self.transaction_costs += transaction_cost

        # Update portfolio value
        self._update_portfolio_value(current_date)

    def _update_portfolio_value(self, current_date):
        """Update the portfolio value."""
        if self.holdings.empty:
            total_value = 0
        else:
            holdings = self.holdings.copy()
            holdings['prices'] = holdings['asset'].apply(
                lambda asset: self.get_price(asset, current_date)
            )
            holdings['value'] = holdings['quantity'] * holdings['prices']
            total_value = holdings['value'].sum()

        new_row = pd.DataFrame([{
            'date': current_date,
            'portfolio_value': total_value
        }])
        self.portfolio_value_history = pd.concat([self.portfolio_value_history, new_row], ignore_index=True)

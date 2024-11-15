from app.analytics.Strategy import Strategy


class Top5MarketCapStrategyAccumulated(Strategy):
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

    def execution(self, current_date, weights):
        """Execute trades based on the calculated weights."""
        trades = []
        transaction_cost = 0
        for asset, weight in weights.items():
            price_row = self.data[
                (self.data['date'] == current_date) & (self.data['asset'] == asset)
            ]
            if price_row.empty:
                continue
            price = price_row['prices'].values[0]
            investment = self.investment_amount * weight
            quantity = investment / price
            trades.append({
                'date': current_date,
                'asset': asset,
                'quantity': quantity,
                'price': price
            })
            self.holdings.add(asset, quantity)
            # Assume transaction cost of 0.1%
            transaction_cost += investment * 0.001
        self.trades.extend(trades)
        self.transaction_costs += transaction_cost
        self._update_portfolio_value(current_date)

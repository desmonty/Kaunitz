from yahooquery import Screener, Ticker

class Yahoo(Screener):
    INTERESTING_INDEXES = [
        '^GSPC',
        '^FTSE'
    ]
    def get_hourly_historical_data(self, symbol: str, period: str='1d'):
        tmp_ticker = Ticker(symbol, asynchronous=True)
        return tmp_ticker.history(
            period=period,
            interval='1h'
        )

if __name__ == '__main__':
    yahoo_api = Yahoo()
    sp500_data = yahoo_api.get_hourly_historical_data('^GSPC')
    print(sp500_data)

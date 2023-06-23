import pandas as pd
import time

from pycoingecko import CoinGeckoAPI

class CoinGecko(CoinGeckoAPI):
    """
    Ceci est une classe permettant l'accès au données de CoinGecko
    """
    def __init__(self):
        super().__init__()

    def get_marketcap_dataframe(self, quote: str='eur', topn: int=250):
        assets = []
        for i in range(1, 2 + topn // 250):
            time.sleep(i)
            assets.extend(self.get_coins_markets(
                vs_currency=quote,
                order='market_cap_desc',
                per_page=250,
                page=i
            ))

        assets = assets[:topn]

        df = pd.DataFrame.from_records(assets)
        df = df[[
            'symbol',
            'current_price',
            'market_cap',
            'total_volume',
            'last_updated'
        ]].rename(columns={
            'current_price': 'price',
            'last_updated': 'created_at'
        })
        df.sort_values(by='market_cap', ascending=False, inplace=True)
        df.reset_index(inplace=True, drop=True)
        df['quote'] = quote
        
        return df

if __name__ == '__main__':
    db = CoinGecko()
    # df = db.get_marketcap_dataframe(topn=10)
    # print(df)

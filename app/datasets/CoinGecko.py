import datetime as dt
import functools
import numpy as np
import pandas as pd
import time
import cytoolz
from pycoingecko import CoinGeckoAPI


class CoinGecko:
    """
    Ceci est une classe permettant l'accès au données de CoinGecko
    """
    def __init__(self):
        self.api = CoinGeckoAPI()
        self.id_to_symbol = None
        self.data_path = 'app/datasets/data_cache'

    def symbol_to_ids(self, symbol: str) -> set:
        """
        Returns the set of ids that maps to the provided symbol
        """
        filename = 'coins_list'
        if self.id_to_symbol is None:
            try:
                df = pd.read_parquet(f'{self.data_path}/{filename}.parquet')
            except:
                coins = self.api.get_coins_list()
                df = pd.DataFrame.from_records(coins)
                df.to_parquet(f'{self.data_path}/{filename}.parquet')
            self.id_to_symbol = dict(zip(df.id, df.symbol))
        
        if symbol in self.id_to_symbol:
            return set([symbol])

        filtered_dict = cytoolz.valfilter(
            lambda x: x == symbol,
            self.id_to_symbol
        )
        return set(filtered_dict.keys())

    def get_marketcap_df(self, quote: str='usd', topn: int=250):
        filename = f"{dt.date.today()}_marketcap_{quote}_top{topn}"
        try:
            return pd.read_parquet(f'{self.data_path}/{filename}.parquet')
        except:
            pass
        assets = []
        for i in range(1, 2 + topn // 250):
            time.sleep(i)
            assets.extend(self.api.get_coins_markets(
                vs_currency=quote,
                order='market_cap_desc',
                per_page=250,
                page=i
            ))

        assets = assets[:topn]

        df = pd.DataFrame.from_records(assets)
        df = df[[
            'id',
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

        df.to_parquet(f'{self.data_path}/{filename}.parquet')
        return df

    def get_historical_df(
        self,
        quote: str='usd',
        topn: int=10,
        days: int=365,
        until: dt.date=dt.date.today()
    ):
        filename = f"{dt.date.today()}_historical_{quote}_top{topn}"
        try:
            return pd.read_parquet(f'{self.data_path}/{filename}.parquet')
        except:
            pass
        
        # Get symbol of top topn assets by marketcap
        df_marketcap = self.get_marketcap_df(quote=quote, topn=topn)
        print(df_marketcap)
        ids = [
            (len(set_ids), set_ids.pop())
            for set_ids in map(self.symbol_to_ids, df_marketcap['id'])
        ]
        # Keep only ids that are not ambiguous
        ids = list(map(lambda x: x[1], filter(lambda x: x[0] == 1, ids)))
        print(ids)

        dfs = []
        to_date = dt.datetime.now(tz=dt.timezone.utc).timestamp()
        from_date = to_date - 86400 * days
        for i, asset_id in enumerate(ids):
            time.sleep((i%30/11.940826)**2)
            records = self.api.get_coin_market_chart_range_by_id(
                id=asset_id,
                from_timestamp=from_date,
                to_timestamp=to_date,
                vs_currency=quote
            )
            df = []
            for metric, data in records.items():
                array_metric = np.array(data)
                array_metric = array_metric.T
                df.append(pd.DataFrame({
                    'timestamp': array_metric[0],
                    metric: array_metric[1]
                }))
            df = functools.reduce(
                lambda left, right: pd.merge(
                    left, right,
                    on = ['timestamp'],
                    how='outer'
                ),
                df
            )
            df['symbol'] = self.id_to_symbol[asset_id]
            df['timestamp'] = df['timestamp'].apply(pd.Timestamp, unit='ms')
            dfs.append(df)
        df = pd.concat(dfs)
        df.reset_index(inplace=True)
        df['quote'] = quote

        df.to_parquet(f'{self.data_path}/{filename}.parquet')
        return df

if __name__ == '__main__':
    db = CoinGecko()
    df = db.get_historical_df(days=15, topn=100)
    print(df)
# tests/test_CoinGeckoClient.py

import pandas as pd
import unittest

from clients.CoinGeckoClient import CoinGeckoClient
from tests.test_data import SUBSET_LIST


EXPECTED_METRICS = ["prices", "total_volumes", "market_caps"]


class TestCoinGeckoClient(unittest.TestCase):
    """Test the CoinGeckoClient class.

    Use SUBSET_LIST which is defined in /tests/test_data.py
    and reflect the state of the information in the /data folder.
    """
    def test_init(self):
        # Init must be called with valid argument for 'subset_id'
        self.assertRaises(Exception, CoinGeckoClient, "invalid_digital_assets")

        for subset_id in SUBSET_LIST:
            self.assertIsInstance(CoinGeckoClient(subset_id), CoinGeckoClient)

    def test_get_market_chart_json(self):
        client = CoinGeckoClient("test")
        valid_asset_id_list = list(client.digital_assets.keys())

        self.assertRaises(TypeError, client.get_market_chart_json) # No argument
        self.assertRaises(TypeError, client.get_market_chart_json, "valid_asset_id_type_but_no_days")
        self.assertRaises(AssertionError, client.get_market_chart_json, {"invalid_asset_id_type"}, 3)
        self.assertRaises(AssertionError, client.get_market_chart_json, "valid_asset_id_type", "invalid_days_type")
        self.assertRaises(Exception, client.get_market_chart_json, "invalid_asset_id", 30)
        self.assertRaises(KeyError, client.get_market_chart_json, "Tezos", 30)

        for asset_id in valid_asset_id_list:
            json_data = client.get_market_chart_json("tezos", 3)
            self.assertIsInstance(json_data, dict)

            for metric in EXPECTED_METRICS:
                self.assertIn(metric, json_data.keys())

    def test_daily_market_data(self):
        client = CoinGeckoClient("test")

        self.assertRaises(TypeError, client.daily_market_data) # No `days` provided
        self.assertRaises(AssertionError, client.daily_market_data, "invalid_days_type")
        self.assertRaises(AssertionError, client.daily_market_data, 0)

        test_days = [1, 2, 3, 4]
        expected_columns = ["dates", "asset_name"] + EXPECTED_METRICS
        for days in test_days:
            self.assertRaises(AssertionError, client.daily_market_data, days, "invalid_metrics_type")
            
            df_market_data = client.daily_market_data(days)
            self.assertIsInstance(df_market_data, pd.DataFrame)

            for col in expected_columns:
                self.assertIn(col, df_market_data.columns)

            num_assets = len(client.digital_assets)
            self.assertEqual(len(df_market_data), num_assets * days)


if __name__ == '__main__':
    unittest.main()
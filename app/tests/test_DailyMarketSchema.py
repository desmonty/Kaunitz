# tests/test_DailyMarketSchema.py

import pandas as pd
import pandera as pa
import unittest

from datetime import datetime, timedelta

from schemas.DailyMarketSchema import DailyMarketSchema


class TestDailyMarketSchema(unittest.TestCase):
    def test_Schema(self):
        df_valid = pd.DataFrame({
            "dates": pd.to_datetime(["2022-08-01", "2022-08-02", "2022-08-03"]),
            "asset_name": ["Cardano", "Cardano", "Cardano"],
            "prices": [0.5, 0.53, 0.49],
            "total_volumes": [10, 11, 13],
            "market_caps": [14, 15, 15]
        })

        self.assertIsInstance(DailyMarketSchema(df_valid), pd.DataFrame)

        df_invalid = df_valid.copy()
        df_invalid.loc[0, "dates"] = datetime.today() + timedelta(2)
        self.assertRaises(pa.errors.SchemaError, DailyMarketSchema, df_invalid)

        df_invalid = df_valid.copy()
        df_invalid.loc[0, "prices"] = -1
        self.assertRaises(pa.errors.SchemaError, DailyMarketSchema, df_invalid)

        df_invalid = df_valid.copy()
        df_invalid.loc[0, "total_volumes"] = "not a number"
        self.assertRaises(pa.errors.SchemaError, DailyMarketSchema, df_invalid)

        df_invalid = df_valid.copy()
        df_invalid.loc[0, "market_caps"] = -1
        self.assertRaises(pa.errors.SchemaError, DailyMarketSchema, df_invalid)


if __name__ == '__main__':
    unittest.main()
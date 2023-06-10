# tests/test_data.py

import json
import unittest

from clients.Client import Client

ID_TYPE_LIST = ["coingecko_id"]
SUBSET_LIST = [None, "random-10", "adaxtz", "test"]


class TestData(unittest.TestCase):
    def test_ID_TYPE_LIST(self):
        with open(Client.DIGITAL_ASSETS_ID_JSON, 'r') as file:
            asset_list = json.load(file)["digital_assets"]
            for asset in asset_list:
                for id_type in ID_TYPE_LIST:
                    self.assertIn(id_type, asset.keys())

    def test_SUBSET_LIST_equivalence(self):
        with open(Client.DIGITAL_ASSETS_SUBSETS_JSON, 'r') as file:
            data_asset_list = json.load(file).keys()

            for asset in data_asset_list:
                self.assertIn(asset, SUBSET_LIST)

            for asset in SUBSET_LIST:
                if asset is not None:
                    self.assertIn(asset, data_asset_list)


if __name__ == '__main__':
    unittest.main()
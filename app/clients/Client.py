# clients/Client.py

import json
import requests

from typing import Optional

class Client(object):
    DIGITAL_ASSETS_ID_JSON = "./data/digital_assets_id.json"
    DIGITAL_ASSETS_SUBSETS_JSON = "./data/digital_assets_subsets.json"

    @classmethod
    def get_json(
        cls,
        url: str,
        headers: Optional[dict[str, str]] = None
    ) -> dict:
        """Wrapper to extract data from an API
        """
        assert isinstance(url, str), f"type(url)={type(url)}!=str"
        assert isinstance(headers, dict) or headers is None,\
               f"type(headers)={type(headers)}!=dict"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise requests.exceptions.HTTPError(
                "An HTTPError occured when sending this URL:\n"
                + f"url: {url}\n"
                + f"error_message: {http_error}"
            )
        except Exception as e:
            raise e

        return response.json()

    @classmethod
    def get_asset_map(
        cls,
        id_type: str,
        subset_id: Optional[str] = None
    ) -> dict:
        """Retun a dict that maps digital assets name to their ids in a
        given framework

        Parameter
        ---------
        id_type : str
            Name of the API to retreive their specific ids e.g. 'coingecko'
        subset_id : str, optional
            Name of the asset subset of interest, if None, take all.
        """
        assert isinstance(id_type, str), f"type(id_type)={type(id_type)}!=str"
        assert isinstance(subset_id, str) or subset_id is None,\
               f"type(subset_id)={type(subset_id)}!=str"

        if not id_type.endswith("_id"):
            id_type += "_id"

        # If subset_id is None, we will return a map for all assets.
        # else, we create a filter that will return true for asset in the subset
        if subset_id is None:
            is_in_subset = lambda _: True
        else:
            with open(Client.DIGITAL_ASSETS_SUBSETS_JSON, 'r') as file:
                asset_subset_list = json.load(file)[subset_id]
                is_in_subset = lambda x: x["name"] in asset_subset_list

        with open(Client.DIGITAL_ASSETS_ID_JSON, 'r') as file:
            asset_list = json.load(file)["digital_assets"]
            digital_assets = {
                asset[id_type]: asset['name']
                for asset in filter(is_in_subset, asset_list)
            }
        return digital_assets
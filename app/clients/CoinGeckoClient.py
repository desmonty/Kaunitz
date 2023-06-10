# clients/CoinGeckoClient.py

import pandas as pd
import json

from datetime import datetime, timedelta
from numbers import Number
from typing import Dict, List, Optional, Tuple

from clients.Client import Client


class CoinGeckoClient(Client):
    """A Client to extract data from the CoinGecko API

    TODO
    ----

    - [ ] Implement retry strategy when applicable
    - [ ] Get 5-minute interval data and ingest in ClickHouse DB,
          schedule to run daily with AirFlow

    """
    def __init__(
        self,
        subset_id: Optional[str] = None,
        vs_currency: str = "usd"
    ):
        """
        Parameters
        ----------
        subset_id : str, optional
            Id of the subset as defined in `Client.DIGITAL_ASSETS_SUBSET_JSON`
            Default value will provide data for all available assets.
        vs_currency : str=usd
            Currency used to display relative information, e.g. "price"
        """
        super(CoinGeckoClient, self).__init__()
        self.vs_currency = vs_currency

        # Get map from CoinGecko specific id to the digital assets name.
        self.digital_assets = self.get_asset_map('coingecko', subset_id)

    def get_market_chart_json(self, asset_id: str, days: int) -> dict:
        """Get information from the /coins/{id}/market_chart endpoint

        Parameters
        ----------
        asset_id : str
            CoinGecko ID of the asset
        days : int
            Timerange limit for the data to extract
        """
        assert isinstance(asset_id, str), f"type(asset_id)={type(asset_id)}!=str"
        assert isinstance(days, int), f"type(days)={type(days)}!=int"

        # This header is required by CoinGecko
        headers = {"accept": "application/json"}

        # Build request following instruction from CoinGecko API documentation
        # https://www.coingecko.com/en/api/documentation
        url = str(
            f"https://api.coingecko.com/api/v3/coins/{asset_id}"
            + f"/market_chart?vs_currency={self.vs_currency}"
            + f"&days={days+1}&interval=daily"
        )

        try:
            return self.get_json(url, headers)
        except Exception as e:
            raise Exception(
                f"Error message: {e}\n"
                + f"Asset Name: {self.digital_assets[asset_id]}\n"
                + f"vs_currency: {self.vs_currency}\n"
                + f"days: {days+1}\n"
            )

    def daily_market_data(
        self,
        days: int,
        metrics: List[str] = ["prices", "market_caps", "total_volumes"]
    ) -> Tuple[pd.DataFrame, Dict[str, Number]]:
        """ Return a pandas dataframe containing market statistics for the
        last {days=30} days for the assets found both in the JSON file and
        using the coingecko API /coins/{id}/market_chart endpoint.
        
        When relevant, data is shown relatively to USD (e.g. for the price
        of the asset).

        Parameters
        ----------
        days : int=30
            Timerange limit for the data to extract
        metrics : list=["prices", "market_caps", "total_volumes"]
            Fill result DataFrame woth those metrics. if they are found in the
            response from a call to the CoinGecko API /coins/{id}/market_chart
            endpoint

        Returns
        -------
        pd.DataFrame
            A dataframe containing market statistics for specific set of
            digital assets.
        """
        assert isinstance(days, int), f"type(days)={type(days)}!=int"
        assert days > 0, "`days` must be greater than 0"
        assert isinstance(metrics, list), f"type(metrics)={type(metrics)}!=list"

        # Create a dataframe containing dates
        df_dates = pd.date_range(
            start=datetime.today() - timedelta(days),
            end=datetime.today() - timedelta(1),
            normalize=True,
            name="dates"
        ).to_frame(index=False)

        # Create a dataframe containing asset_name    
        df_assets = pd.DataFrame({"asset_name": self.digital_assets.keys()})

        # Merge df_dates with a dataframe containing assets name
        # to get a dataframe with one row for each combinaison:
        # 'dates' x 'asset_name'
        df_results = df_dates.merge(df_assets, how='cross')

        # Append result DataFrame to this list before final concat.
        list_dataframes_result = []

        # For each asset in the dict, we try to get the data from the API
        # and raise an exception at the first encountered error.
        for asset_id, asset_name in self.digital_assets.items():
            # Request data from the CoinGecko API
            json_data = self.get_market_chart_json(asset_id, days)

            # DataFrame containing all the dates for which we request data such
            # that information associated to other dates will not be taken into
            # account and missing data will generate NAs in the final DataFrame
            df_result_asset = df_dates

            # We make sure to only take specific metrics
            is_valid_metric = lambda x: x in metrics
            for metric in filter(is_valid_metric, json_data.keys()):
                tmp_dates = [
                    pd.to_datetime(elem[0], unit='ms').normalize()
                    for elem in json_data[metric]
                ]
                tmp_metric = [elem[1] for elem in json_data[metric]]
                df_tmp = pd.DataFrame({
                    "dates": tmp_dates,
                    metric: tmp_metric
                })

                # Remove duplicate on dates by keeping last value
                df_tmp = df_tmp.sort_values(['dates']).groupby('dates').tail(1)
                df_tmp.reset_index(drop=True, inplace=True)

                df_result_asset = pd.merge(
                    df_result_asset,
                    df_tmp,
                    how='left',
                    on="dates"
                )

            # Add an empty column for all missing metrics
            is_absent_from_json_data = lambda x: x not in json_data.keys()
            for metric in filter(is_absent_from_json_data, metrics):
                df_result_asset[metric] = None

            # Add the asset name in the DataFrame
            df_result_asset["asset_name"] = asset_name

            # Append the DataFrame to the list 
            list_dataframes_result.append(df_result_asset)

        # Result data frame is a concatenation of all retreived data frame
        return pd.concat(list_dataframes_result)
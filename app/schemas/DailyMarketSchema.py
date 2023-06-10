# schemas/DailyMarketSchema.py

import pandas as pd
import pandera as pa

from datetime import datetime
from pandera.typing import Series
from pandera.dtypes import Timestamp
from typing import Dict


class DailyMarketSchema(pa.SchemaModel):
    dates: Series[Timestamp] = pa.Field(
        lt=datetime.today(),
        coerce=True,
        nullable=False
    )
    asset_name: Series[str] = pa.Field(
        coerce=True,
        nullable=False
    )
    prices: Series[float] = pa.Field(
        ge=0, 
        coerce=True,
        nullable=True
    )
    total_volumes: Series[float] = pa.Field(
        ge=0, 
        coerce=True,
        nullable=True
    )
    market_caps: Series[float] = pa.Field(
        ge=0, 
        coerce=True,
        nullable=True
    )

    @pa.check(
        "asset_name",
        groupby="dates",
        name="check_dates_has_uniform_asset"
    )
    def check_asset_groupby_dates_unique(
        cls,
        grouped_values: Dict[Timestamp, Series[str]]
    ) -> bool:
        return all([
            len(col) == len(col.unique())
            for col in grouped_values.values()
        ])

    @pa.check(
        "asset_name",
        groupby="dates",
        name="check_dates_has_same_number_assets"
    )
    def check_asset_groupby_dates_same_number(
        cls,
        grouped_values: Dict[Timestamp, Series[str]]
    ) -> bool:
        nassets = pd.Series([col.nunique() for col in grouped_values.values()])
        return nassets.nunique() == 1
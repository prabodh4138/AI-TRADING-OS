from __future__ import annotations

import pandas as pd


class IndicatorLoader:
    """Loads market data for indicator calculation."""

    def load(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare and validate market data before calculation.
        """
        if data.empty:
            raise ValueError("No market data available.")

        return data.sort_values("trading_date").reset_index(drop=True)
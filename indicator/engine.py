from __future__ import annotations

import pandas as pd

from dto.indicator_dto import IndicatorDTO


class IndicatorEngine:
    """Indicator calculation engine."""

    def calculate(self, data: pd.DataFrame) -> list[IndicatorDTO]:
        """
        Calculate indicators from OHLCV data.

        Implementation will be added in the next step.
        """
        return []
"""
Test Indicator Calculator
"""

from database.unit_of_work import UnitOfWork
from indicator.loader import IndicatorLoader
from indicator.calculator import IndicatorCalculator

import pandas as pd


def main():

    with UnitOfWork() as uow:

        # ---------------------------------------------------------
        # Get first available symbol
        # ---------------------------------------------------------
        symbol_ids = uow.market_data.get_all_symbol_ids()

        if not symbol_ids:
            print("No symbols found.")
            return

        symbol_id = symbol_ids[0]

        print(f"\nSymbol ID : {symbol_id}")

        # ---------------------------------------------------------
        # Load complete market history
        # ---------------------------------------------------------
        records = uow.market_data.get_price_history_by_symbol(symbol_id)

        print(f"Market Records : {len(records)}")

        if not records:
            print("No market data found.")
            return

        # ---------------------------------------------------------
        # Convert SQLAlchemy objects to Pandas DataFrame
        # ---------------------------------------------------------
        data = [
            {
                "trading_date": r.trading_date,
                "open": float(r.open_price),
                "high": float(r.high_price),
                "low": float(r.low_price),
                "close": float(r.close_price),
                "volume": int(r.volume),
            }
            for r in records
        ]

        df = pd.DataFrame(data)

        # Ensure chronological order
        df = df.sort_values("trading_date").reset_index(drop=True)

        print("\nInput DataFrame Shape :", df.shape)

        print("\nInput Columns:")
        print(df.columns.tolist())

        # ---------------------------------------------------------
        # Validate Data
        # ---------------------------------------------------------
        loader = IndicatorLoader()

        df = loader.load(df)

        # ---------------------------------------------------------
        # Calculate Indicators
        # ---------------------------------------------------------
        calculator = IndicatorCalculator()

        df = calculator.calculate(df)

        print("\nOutput DataFrame Shape :", df.shape)

        print("\nGenerated Columns:")

        for column in df.columns:
            print(f"  {column}")

        print("\nLast 5 Records:")

        print(df.tail())


if __name__ == "__main__":
    main()
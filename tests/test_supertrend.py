"""
AI Trading OS
SuperTrend Validation Test
"""

from database.unit_of_work import UnitOfWork
from indicator.loader import IndicatorLoader
from indicator.calculator import IndicatorCalculator

import pandas as pd


def main():

    with UnitOfWork() as uow:

        symbol_ids = uow.market_data.get_all_symbol_ids()

        if not symbol_ids:
            print("No symbols found.")
            return

        symbol_id = symbol_ids[0]

        print("=" * 80)
        print("SUPER TREND VALIDATION")
        print("=" * 80)

        print(f"Symbol : {symbol_id}")

        records = uow.market_data.get_price_history_by_symbol(symbol_id)

        print(f"Records : {len(records)}")

        df = pd.DataFrame([
            {
                "trading_date": r.trading_date,
                "open": float(r.open_price),
                "high": float(r.high_price),
                "low": float(r.low_price),
                "close": float(r.close_price),
                "volume": int(r.volume),
            }
            for r in records
        ])

        df = df.sort_values("trading_date").reset_index(drop=True)

        loader = IndicatorLoader()

        df = loader.load(df)

        calculator = IndicatorCalculator()

        df = calculator.calculate(df)

        print("\n")

        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)

        print(f"Rows                  : {len(df)}")
        print(f"SuperTrend NaN        : {df['supertrend'].isna().sum()}")
        print(f"Direction Values      : {sorted(df['supertrend_direction'].unique())}")

        print("\n")

        print("=" * 80)
        print("LAST 20 ROWS")
        print("=" * 80)

        print(
            df[
                [
                    "trading_date",
                    "close",
                    "atr14",
                    "supertrend",
                    "supertrend_direction",
                ]
            ].tail(20)
        )

        print("\n")

        print("=" * 80)
        print("TREND CHANGES")
        print("=" * 80)

        changes = df[
            df["supertrend_direction"]
            != df["supertrend_direction"].shift()
        ]

        print(changes[
            [
                "trading_date",
                "close",
                "supertrend",
                "supertrend_direction",
            ]
        ])

        print("\n")

        print("=" * 80)
        print("VALIDATION")
        print("=" * 80)

        if df["supertrend"].isna().all():

            print("❌ FAIL : SuperTrend is completely NaN")

        elif df["supertrend"].isna().sum() > 20:

            print("⚠ WARNING : Too many NaN values")

        else:

            print("✅ SuperTrend Generated")

        print()

        print("Done.")


if __name__ == "__main__":
    main()
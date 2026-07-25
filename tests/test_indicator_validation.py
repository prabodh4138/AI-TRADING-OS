"""
AI Trading OS
Indicator Validation Test
"""

from wsgiref.validate import validator

from database.unit_of_work import UnitOfWork
from indicator.loader import IndicatorLoader
from indicator.calculator import IndicatorCalculator

import numpy as np
import pandas as pd


class Validator:

    def __init__(self):
        self.results = []

    def check(self, name, condition, details=""):

        status = "PASS" if condition else "FAIL"

        self.results.append(
            (name, status, details)
        )

    def report(self):

        print("\n")
        print("=" * 80)
        print("INDICATOR VALIDATION REPORT")
        print("=" * 80)

        passed = 0

        for name, status, details in self.results:

            print(f"{name:<30}{status:<8}{details}")

            if status == "PASS":
                passed += 1

        print("=" * 80)

        print(
            f"Passed : {passed}/{len(self.results)}"
        )

        if passed == len(self.results):

            print("\n✅ ALL VALIDATIONS PASSED")

        else:

            print("\n❌ VALIDATION FAILED")


def main():

    validator = Validator()

    with UnitOfWork() as uow:

        symbol = uow.market_data.get_all_symbol_ids()[0]

        rows = uow.market_data.get_price_history_by_symbol(symbol)

        df = pd.DataFrame(
            [
                {
                    "trading_date": r.trading_date,
                    "open": float(r.open_price),
                    "high": float(r.high_price),
                    "low": float(r.low_price),
                    "close": float(r.close_price),
                    "volume": float(r.volume),
                }
                for r in rows
            ]
        )

    df = IndicatorLoader().load(df)

    df = IndicatorCalculator().calculate(df)

    # -------------------------------------------------
    # General
    # -------------------------------------------------

    validator.check(
        "Rows Loaded",
        len(df) > 100,
        f"Rows={len(df)}",
    )

    # -------------------------------------------------
    # SMA
    # -------------------------------------------------

    validator.check(
        "SMA20",
        df["sma20"].dropna().between(
            df["low"].min(),
            df["high"].max(),
        ).all(),
    )

    validator.check(
        "SMA50",
        df["sma50"].dropna().between(
            df["low"].min(),
            df["high"].max(),
        ).all(),
    )

    # -------------------------------------------------
    # EMA
    # -------------------------------------------------

    validator.check(
        "EMA20",
        df["ema20"].dropna().between(
            df["low"].min(),
            df["high"].max(),
        ).all(),
    )

    validator.check(
        "EMA50",
        df["ema50"].dropna().between(
            df["low"].min(),
            df["high"].max(),
        ).all(),
    )

    # -------------------------------------------------
    # RSI
    # -------------------------------------------------

    validator.check(
        "RSI14",
        df["rsi14"].dropna().between(0, 100).all(),
    )

    # -------------------------------------------------
    # ATR
    # -------------------------------------------------

    validator.check(
        "ATR14",
        (df["atr14"].dropna() >= 0).all(),
    )

    # -------------------------------------------------
    # ADX
    # -------------------------------------------------

    validator.check(
        "ADX14",
        df["adx14"].dropna().between(0, 100).all(),
    )

    # -------------------------------------------------
    # DI
    # -------------------------------------------------

    validator.check(
        "PLUS_DI",
        df["plus_di"].dropna().between(0, 100).all(),
    )

    validator.check(
        "MINUS_DI",
        df["minus_di"].dropna().between(0, 100).all(),
    )

    # -------------------------------------------------
    # Bollinger
    # -------------------------------------------------

    bb = df[
    ["bb_upper", "bb_middle", "bb_lower"]
        ].dropna()

    validator.check(
    "BB Upper",
    (bb["bb_upper"] >= bb["bb_middle"]).all(),
    )

    validator.check(
    "BB Lower",
    (bb["bb_lower"] <= bb["bb_middle"]).all(),
    )

    validator.check(
    "BB Width",
    (bb["bb_upper"] >= bb["bb_lower"]).all(),
    )

    # -------------------------------------------------
    # OBV
    # -------------------------------------------------

    validator.check(
        "OBV",
        ~df["obv"].isna().all(),
    )

    # -------------------------------------------------
    # Relative Volume
    # -------------------------------------------------

    validator.check(
        "Relative Volume",
        (df["relative_volume"].dropna() >= 0).all(),
    )

    # -------------------------------------------------
    # ROC
    # -------------------------------------------------

    validator.check(
        "ROC",
        ~df["roc10"].isna().all(),
    )

    # -------------------------------------------------
    # Momentum
    # -------------------------------------------------

    validator.check(
        "Momentum",
        ~df["momentum10"].isna().all(),
    )

    # -------------------------------------------------
    # Stochastic
    # -------------------------------------------------

    validator.check(
        "Stochastic K",
        df["stochastic_k"].dropna().between(
            0,
            100,
        ).all(),
    )

    validator.check(
        "Stochastic D",
        df["stochastic_d"].dropna().between(
            0,
            100,
        ).all(),
    )
    print("\n========== BOLLINGER DEBUG ==========")
    print(df[["trading_date", "close", "bb_upper", "bb_middle", "bb_lower"]].tail(20))

    bb = df[["bb_upper", "bb_middle", "bb_lower"]].dropna()

    print("\nRows where Upper < Middle:")
    print(bb[bb["bb_upper"] < bb["bb_middle"]])

    print("\nRows where Lower > Middle:")
    print(bb[bb["bb_lower"] > bb["bb_middle"]])       
    validator.report()


if __name__ == "__main__":
    main()
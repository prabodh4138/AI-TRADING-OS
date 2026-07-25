"""
AI Trading Operating System
Market Data CRUD Test
"""

from __future__ import annotations

from datetime import date

from database.models.market_data import MarketData
from database.models.symbol import Symbol
from database.repositories.market_data_repository import MarketDataRepository
from database.repositories.symbol_repository import SymbolRepository
from database.session import get_session


def main():

    with get_session() as session:

        symbol_repo = SymbolRepository(session)
        market_repo = MarketDataRepository(session)

        print("=" * 70)
        print("MARKET DATA CRUD TEST")
        print("=" * 70)

        # ---------------------------------------------------------
        # Get or Create Symbol
        # ---------------------------------------------------------

        symbol = symbol_repo.get_by_symbol_code("RELIANCE")

        if symbol is None:

            symbol = Symbol(
                symbol_code="RELIANCE",
                symbol_name="Reliance Industries Ltd",
                exchange="NSE",
                instrument_type="EQ",
                sector="Energy",
                industry="Oil & Gas",
                isin="INE002A01018",
                lot_size=1,
                tick_size=0.05,
                face_value=10,
                is_fno=True,
            )

            symbol_repo.add(symbol)
            symbol_repo.flush()

            print("✓ Created RELIANCE")

        # ---------------------------------------------------------
        # Insert Market Data
        # ---------------------------------------------------------

        market = MarketData(

            symbol_id=symbol.symbol_id,

            trading_date=date(2026, 7, 24),

            open_price=1500.00,
            high_price=1525.00,
            low_price=1490.00,
            close_price=1518.50,

            adjusted_close=1518.50,

            volume=1523456,

            delivery_volume=985000,

            delivery_percent=64.67,

            turnover=2315000000,

            vwap=1512.25,

            trade_count=185432,
        )

        market_repo.add(market)
        market_repo.flush()

        print("✓ Market data inserted")

        # ---------------------------------------------------------
        # Latest Price
        # ---------------------------------------------------------

        latest = market_repo.get_latest_price(symbol.symbol_id)

        print("\nLatest Price")
        print("-------------------------")
        print("Date  :", latest.trading_date)
        print("Close :", latest.close_price)

        # ---------------------------------------------------------
        # History
        # ---------------------------------------------------------

        history = market_repo.get_price_history(
            symbol.symbol_id,
            date(2026, 7, 1),
            date(2026, 7, 31),
        )

        print("\nHistory Count :", len(history))

        print("\n✓ MARKET DATA CRUD PASSED")


if __name__ == "__main__":
    main()
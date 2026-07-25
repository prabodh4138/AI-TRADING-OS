"""
AI Trading Operating System
Symbol CRUD Test
"""

from __future__ import annotations

from database.models.symbol import Symbol
from database.repositories.symbol_repository import SymbolRepository
from database.session import get_session


def main():

    with get_session() as session:

        repo = SymbolRepository(session)

        print("=" * 70)
        print("SYMBOL CRUD TEST")
        print("=" * 70)

        # ----------------------------------------------------------
        # Create
        # ----------------------------------------------------------

        symbol = Symbol(
            symbol_code="RELIANCE",
            symbol_name="Reliance Industries Ltd",
            exchange="NSE",
            instrument_type="EQ",
            sector="Oil & Gas",
            industry="Refineries",
            isin="INE002A01018",
            lot_size=1,
            tick_size=0.05,
            face_value=10,
            is_fno=True,
        )

        repo.add(symbol)
        repo.flush()

        print("✓ Symbol Inserted")
        print("UUID :", symbol.symbol_id)

        # ----------------------------------------------------------
        # Read
        # ----------------------------------------------------------

        db_symbol = repo.get_by_symbol_code("RELIANCE")

        print("\nRetrieved Symbol")

        print("------------------------")
        print("Code :", db_symbol.symbol_code)
        print("Name :", db_symbol.symbol_name)
        print("Exchange :", db_symbol.exchange)

        # ----------------------------------------------------------
        # Update
        # ----------------------------------------------------------

        db_symbol.sector = "Energy"

        repo.flush()

        print("\n✓ Updated Sector")

        # ----------------------------------------------------------
        # Count
        # ----------------------------------------------------------

        print("\nTotal Symbols :", repo.count())

        # ----------------------------------------------------------
        # Delete
        # ----------------------------------------------------------

        repo.delete(db_symbol)

        repo.flush()

        print("✓ Symbol Deleted")

        print("\nRemaining Symbols :", repo.count())


if __name__ == "__main__":
    main()
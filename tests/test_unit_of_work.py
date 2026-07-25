"""
AI Trading Operating System
Unit Of Work Test
"""

from database.models.symbol import Symbol
from database.unit_of_work import UnitOfWork


def main():

    print("=" * 70)
    print("UNIT OF WORK TEST")
    print("=" * 70)

    with UnitOfWork() as uow:

        symbol = uow.symbols.get_by_symbol_code("TCS")

        if symbol is None:

            symbol = Symbol(

                symbol_code="TCS",

                symbol_name="Tata Consultancy Services",

                exchange="NSE",

                instrument_type="EQ",

                sector="IT",

                industry="Software",

                isin="INE467B01029",

                lot_size=1,

                tick_size=0.05,

                face_value=1,

                is_fno=True,

            )

            uow.symbols.add(symbol)

            print("✓ TCS Inserted")

        else:

            print("✓ TCS Already Exists")

        print()

        print("Total Symbols :", uow.symbols.count())


if __name__ == "__main__":
    main()
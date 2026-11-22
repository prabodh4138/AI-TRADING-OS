from sqlalchemy import text
from database.connection import database

with database.engine.connect() as conn:
    print("TOTAL:", conn.execute(
        text("SELECT COUNT(*) FROM symbol")
    ).scalar())

    print("EQ:", conn.execute(
        text("SELECT COUNT(*) FROM symbol WHERE series = 'EQ'")
    ).scalar())

    print("BE:", conn.execute(
        text("SELECT COUNT(*) FROM symbol WHERE series = 'BE'")
    ).scalar())

    print("NULL SERIES:", conn.execute(
        text("SELECT COUNT(*) FROM symbol WHERE series IS NULL")
    ).scalar())

    print("20MICRONS:", conn.execute(
        text("""
            SELECT symbol_code, series, isin
            FROM symbol
            WHERE symbol_code = '20MICRONS'
        """)
    ).fetchone())

    print("360ONE:", conn.execute(
        text("""
            SELECT symbol_code, series, isin
            FROM symbol
            WHERE symbol_code = '360ONE'
        """)
    ).fetchone())

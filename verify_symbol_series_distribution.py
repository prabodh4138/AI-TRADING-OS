from sqlalchemy import text
from database.connection import database

with database.engine.connect() as conn:
    rows = conn.execute(
        text("""
            SELECT
                COALESCE(series, '<NULL>') AS series,
                COUNT(*) AS symbol_count
            FROM symbol
            GROUP BY series
            ORDER BY symbol_count DESC, series
        """)
    ).all()

print("NSE SERIES DISTRIBUTION")
print("-" * 35)

for series, count in rows:
    print(f"{series}: {count}")

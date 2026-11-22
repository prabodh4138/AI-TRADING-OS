from sqlalchemy import text
from database.connection import database

with database.engine.connect() as conn:
    print("DATABASE:", conn.execute(text("SELECT current_database()")).scalar())
    print("SCHEMA:", conn.execute(text("SELECT current_schema()")).scalar())

    print("TABLES:")
    tables = conn.execute(
        text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
    ).scalars().all()

    for table in tables:
        print("  ", table)

    print("ALEMBIC:", conn.execute(
        text("SELECT version_num FROM alembic_version")
    ).scalar())

"""
Temporary Test
Database Session Verification

NOTE:
This file is temporary.
It will be removed after Build-04 is completed.
"""

from sqlalchemy import text

from database.session import get_session


def main() -> None:
    try:
        with get_session() as session:
            version = session.execute(text("SELECT version();")).scalar()

            print("=" * 60)
            print("Database Session Test")
            print("=" * 60)
            print(f"PostgreSQL Version : {version}")
            print()
            print("✅ Session Factory : OK")
            print("✅ Transaction     : OK")
            print("✅ Database Access : OK")
            print("=" * 60)

    except Exception as exc:
        print()
        print("❌ Database Session Test Failed")
        print(exc)
        raise


if __name__ == "__main__":
    main()
"""
Temporary Test
Verify SQLAlchemy Declarative Base
"""

from database.base import Base


def main() -> None:
    print("=" * 60)
    print("Declarative Base Test")
    print("=" * 60)
    print()

    print("Base Class :", Base)

    print()
    print("✅ Declarative Base : OK")
    print("=" * 60)


if __name__ == "__main__":
    main()
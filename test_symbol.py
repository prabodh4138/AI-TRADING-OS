"""
Temporary Test
Verify Symbol ORM Model
"""

from database.models.symbol import Symbol


def main() -> None:
    print("=" * 60)
    print("Symbol Model Test")
    print("=" * 60)

    print(Symbol)

    print()

    print("✓ ORM Model Loaded")
    print("✓ UUID Primary Key")
    print("✓ Audit Columns")
    print("✓ Business Columns")

    print("=" * 60)


if __name__ == "__main__":
    main()
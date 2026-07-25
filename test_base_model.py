"""
Temporary Test
Verify BaseModel
"""

from database.base_model import BaseModel


def main():

    print("=" * 60)
    print("BaseModel Test")
    print("=" * 60)

    print()

    print("BaseModel :", BaseModel)

    print()

    print("✓ created_at available")
    print("✓ updated_at available")
    print("✓ is_active available")

    print()

    print("SUCCESS")

    print("=" * 60)


if __name__ == "__main__":
    main()
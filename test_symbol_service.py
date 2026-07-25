from database.session import get_session
from services.symbol_service import SymbolService


def main():

    with get_session() as session:

        service = SymbolService(session)

        print(service)

        print("✓ Symbol Service Created")


if __name__ == "__main__":
    main()
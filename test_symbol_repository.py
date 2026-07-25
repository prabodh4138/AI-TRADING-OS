from database.session import get_session
from database.repositories.symbol_repository import SymbolRepository


def main():

    with get_session() as session:

        repo = SymbolRepository(session)

        print(repo)


if __name__ == "__main__":
    main()
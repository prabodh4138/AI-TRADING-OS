from database.session import get_session
from database.repositories.symbol_repository import SymbolRepository
from database.repositories.market_data_repository import MarketDataRepository


def main():

    with get_session() as session:

        symbol_repo = SymbolRepository(session)
        market_repo = MarketDataRepository(session)

        print("=" * 60)
        print("AI Trading OS Repository Test")
        print("=" * 60)

        print("Symbol Count      :", symbol_repo.count())
        print("Market Data Count :", market_repo.count())


if __name__ == "__main__":
    main()
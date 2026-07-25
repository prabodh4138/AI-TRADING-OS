from database.unit_of_work import UnitOfWork


def main():

    with UnitOfWork() as uow:

        symbols = uow.market_data.get_all_symbol_ids()

        print(f"Symbols : {len(symbols)}")

        if symbols:

            print(symbols[:10])

            history = uow.market_data.get_price_history_by_symbol(
                symbols[0]
            )

            print(
                f"Records : {len(history)}"
            )


if __name__ == "__main__":
    main()
from dto.symbol_dto import SymbolCreateDTO
from services.symbol_service import SymbolService


def main():

    service = SymbolService()

    dto = SymbolCreateDTO(
        symbol_code="INFY",
        symbol_name="Infosys Limited",
        exchange="NSE",
        instrument_type="EQ",
        sector="IT",
        industry="Software",
        isin="INE009A01021",
        lot_size=1,
        tick_size=0.05,
        face_value=5,
        is_fno=True,
    )

    try:

        symbol = service.create_symbol(dto)

        print("✓ Created :", symbol.symbol_code)

    except Exception as e:

        print("Error :", e)


if __name__ == "__main__":
    main()
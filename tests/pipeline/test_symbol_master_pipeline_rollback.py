from pathlib import Path
from unittest.mock import Mock

import pandas as pd

from database.repositories.import_batch_repository import ImportBatchRepository
from database.repositories.symbol_repository import SymbolRepository
from data_engine.pipeline import symbol_master_pipeline as pipeline_module
from data_engine.pipeline.symbol_master_pipeline import SymbolMasterPipeline


class ControlledUnitOfWork:
    """
    Uses the pytest database session so the pipeline transaction
    can be inspected directly.
    """

    def __init__(self, session):
        self.session = session
        self.symbols = SymbolRepository(session)
        self.import_batches = ImportBatchRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.session.rollback()
            return False

        self.session.commit()
        return False


def test_symbol_master_pipeline_rolls_back_on_database_failure(
    db_session,
    monkeypatch,
):
    loader = Mock()
    validator = Mock()
    transformer = Mock()
    logger = Mock()

    source_df = pd.DataFrame(
        {
            "SYMBOL": ["ROLLBACK_TEST"],
            "NAME OF COMPANY": ["Rollback Test Limited"],
            "SERIES": ["EQ"],
            "DATE OF LISTING": ["01-JAN-2020"],
            "PAID UP VALUE": [10],
            "MARKET LOT": [1],
            "ISIN NUMBER": ["INEROLLBACK01"],
            "FACE VALUE": [10],
        }
    )

    transformed_df = pd.DataFrame(
        {
            "symbol_code": ["ROLLBACK_TEST"],
            "company_name": ["Rollback Test Limited"],
            "series": ["EQ"],
            "listing_date": ["2020-01-01"],
            "paid_up_value": [10],
            "market_lot": [1],
            "isin": ["INEROLLBACK01"],
            "face_value": [10],
        }
    )

    loader.load.return_value = source_df
    validator.validate.return_value = source_df
    transformer.transform.return_value = transformed_df

    class FailingService:
        def import_dataframe(self, dataframe, uow):
            uow.symbols.bulk_upsert(
                [
                    {
                        "symbol_code": "ROLLBACK_TEST",
                        "symbol_name": "Rollback Test Limited",
                        "exchange": "NSE",
                        "instrument_type": "EQUITY",
                        "isin": "INEROLLBACK01",
                        "lot_size": 1,
                        "tick_size": 0.05,
                        "face_value": 10,
                        "listing_date": None,
                        "sector": None,
                        "industry": None,
                        "is_fno": False,
                    }
                ]
            )

            raise RuntimeError("forced database failure")

    service = FailingService()

    monkeypatch.setattr(
        pipeline_module,
        "UnitOfWork",
        lambda: ControlledUnitOfWork(db_session),
    )

    pipeline = SymbolMasterPipeline(
        loader=loader,
        validator=validator,
        transformer=transformer,
        service=service,
        logger=logger,
    )

    result = pipeline.import_csv(Path("rollback_test.csv"))

    assert result.success is False
    assert result.rows_read == 1
    assert result.rows_imported == 0
    assert result.rows_failed == 1
    assert "forced database failure" in result.exception

    symbol_repository = SymbolRepository(db_session)

    assert (
        symbol_repository.get_by_symbol_code("ROLLBACK_TEST")
        is None
    )

    import_batch_repository = ImportBatchRepository(db_session)

    batches = import_batch_repository.list_batches()

    assert all(
        batch.batch_name != "NSE_SYMBOL_MASTER"
        for batch in batches
    )

from datetime import date
from pathlib import Path
from unittest.mock import Mock

import pandas as pd

from data_engine.pipeline.symbol_master_pipeline import SymbolMasterPipeline
import pytest


@pytest.fixture(autouse=True)
def mock_unit_of_work(monkeypatch):
    mock_uow = Mock()
    mock_uow.__enter__ = Mock(return_value=mock_uow)
    mock_uow.__exit__ = Mock(return_value=None)
    mock_uow.symbols = Mock()
    mock_uow.import_batches = Mock()
    mock_batch = Mock()
    mock_batch.batch_id = "mock-batch-id"
    mock_exec = Mock()
    mock_exec.execution_id = "mock-exec-id"
    monkeypatch.setattr("data_engine.pipeline.symbol_master_pipeline.UnitOfWork", lambda: mock_uow)
    monkeypatch.setattr("data_engine.pipeline.symbol_master_pipeline.ImportBatchService", Mock(return_value=Mock(
        start_batch=Mock(return_value=mock_batch),
        register_execution=Mock(return_value=mock_exec),
        start_execution=Mock(),
        finish_execution=Mock(),
        complete_batch=Mock()
    )))


def test_symbol_master_pipeline_success():
    loader = Mock()
    validator = Mock()
    transformer = Mock()
    service = Mock()
    logger = Mock()

    source_df = pd.DataFrame(
        {
            "SYMBOL": ["ABC", "XYZ"],
            "NAME OF COMPANY": ["ABC Limited", "XYZ Limited"],
            "SERIES": ["EQ", "EQ"],
            "DATE OF LISTING": ["01-JAN-2020", "02-FEB-2021"],
            "PAID UP VALUE": [10, 10],
            "MARKET LOT": [1, 1],
            "ISIN NUMBER": ["INE000A01001", "INE000B01002"],
            "FACE VALUE": [10, 10],
        }
    )

    transformed_df = pd.DataFrame(
        {
            "symbol_code": ["ABC", "XYZ"],
            "company_name": ["ABC Limited", "XYZ Limited"],
            "series": ["EQ", "EQ"],
            "listing_date": [date(2020, 1, 1), date(2021, 2, 2)],
            "paid_up_value": [10, 10],
            "market_lot": [1, 1],
            "isin": ["INE000A01001", "INE000B01002"],
            "face_value": [10, 10],
        }
    )

    loader.load.return_value = source_df
    validator.validate.return_value = source_df
    transformer.transform.return_value = transformed_df
    service.import_dataframe.return_value = {
        "new": 2,
        "updated": 0,
        "affected": 2,
    }

    pipeline = SymbolMasterPipeline(
        loader=loader,
        validator=validator,
        transformer=transformer,
        service=service,
        logger=logger,
    )

    result = pipeline.import_csv(Path("EQUITY_L.csv"))

    assert result.success is True
    assert result.rows_read == 2
    assert result.rows_imported == 2
    assert result.rows_failed == 0
    assert result.file_name == "EQUITY_L.csv"

    loader.load.assert_called_once()
    validator.validate.assert_called_once()
    transformer.transform.assert_called_once()
    service.import_dataframe.assert_called_once()


def test_symbol_master_pipeline_file_not_found():
    loader = Mock()
    validator = Mock()
    transformer = Mock()
    service = Mock()
    logger = Mock()

    loader.load.side_effect = FileNotFoundError("file not found")

    pipeline = SymbolMasterPipeline(
        loader=loader,
        validator=validator,
        transformer=transformer,
        service=service,
        logger=logger,
    )

    result = pipeline.import_csv(Path("missing.csv"))

    assert result.success is False
    assert result.rows_read == 0
    assert result.rows_imported == 0
    assert result.rows_failed == 0
    assert result.file_name == "missing.csv"

    validator.validate.assert_not_called()
    transformer.transform.assert_not_called()
    service.import_dataframe.assert_not_called()


def test_symbol_master_pipeline_validation_failure():
    loader = Mock()
    validator = Mock()
    transformer = Mock()
    service = Mock()
    logger = Mock()

    source_df = pd.DataFrame({"SYMBOL": ["ABC"]})

    loader.load.return_value = source_df
    validator.validate.side_effect = ValueError("invalid symbol master")

    pipeline = SymbolMasterPipeline(
        loader=loader,
        validator=validator,
        transformer=transformer,
        service=service,
        logger=logger,
    )

    result = pipeline.import_csv(Path("bad.csv"))

    assert result.success is False
    assert result.rows_read == 1
    assert result.rows_imported == 0
    assert result.rows_failed == 1

    transformer.transform.assert_not_called()
    service.import_dataframe.assert_not_called()


def test_symbol_master_pipeline_latest_csv(tmp_path):
    older = tmp_path / "older.csv"
    latest = tmp_path / "latest.csv"

    older.write_text("old")
    latest.write_text("new")

    loader = Mock()
    validator = Mock()
    transformer = Mock()
    service = Mock()
    logger = Mock()

    source_df = pd.DataFrame(
        {
            "SYMBOL": ["ABC"],
            "NAME OF COMPANY": ["ABC Limited"],
            "SERIES": ["EQ"],
            "DATE OF LISTING": ["01-JAN-2020"],
            "PAID UP VALUE": [10],
            "MARKET LOT": [1],
            "ISIN NUMBER": ["INE000A01001"],
            "FACE VALUE": [10],
        }
    )

    transformed_df = pd.DataFrame(
        {
            "symbol_code": ["ABC"],
            "company_name": ["ABC Limited"],
            "series": ["EQ"],
            "listing_date": [date(2020, 1, 1)],
            "paid_up_value": [10],
            "market_lot": [1],
            "isin": ["INE000A01001"],
            "face_value": [10],
        }
    )

    loader.load.return_value = source_df
    validator.validate.return_value = source_df
    transformer.transform.return_value = transformed_df
    service.import_dataframe.return_value = {
        "new": 1,
        "updated": 0,
        "affected": 1,
    }

    pipeline = SymbolMasterPipeline(
        loader=loader,
        validator=validator,
        transformer=transformer,
        service=service,
        logger=logger,
    )

    result = pipeline.import_latest_csv(tmp_path)

    assert result.success is True
    loader.load.assert_called_once_with(latest)


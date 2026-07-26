"""
Unit tests for ImportService.

These tests verify that ImportService correctly orchestrates
the import pipeline by coordinating its dependencies.

The actual implementations of the loader, validator,
transformer and persistence layer are mocked so that
these tests remain fast and isolated.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from dto.import_statistics import ImportStatistics
from services.import_service import ImportService


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def mock_loader() -> Mock:
    """Mock CSVLoader."""
    return Mock()


@pytest.fixture
def mock_validator() -> Mock:
    """Mock CSVValidator."""
    return Mock()


@pytest.fixture
def mock_transformer() -> Mock:
    """Mock DataTransformer."""
    return Mock()


@pytest.fixture
def mock_market_data_service() -> Mock:
    """Mock MarketDataService."""
    return Mock()


@pytest.fixture
def import_service(
    mock_loader: Mock,
    mock_validator: Mock,
    mock_transformer: Mock,
    mock_market_data_service: Mock,
) -> ImportService:
    """
    Create an ImportService with mocked dependencies.
    """

    return ImportService(
        loader=mock_loader,
        validator=mock_validator,
        transformer=mock_transformer,
        market_data_service=mock_market_data_service,
    )


# ----------------------------------------------------------------------
# Basic construction tests
# ----------------------------------------------------------------------


def test_import_service_initialization(
    import_service: ImportService,
    mock_loader: Mock,
    mock_validator: Mock,
    mock_transformer: Mock,
    mock_market_data_service: Mock,
) -> None:
    """
    ImportService should retain injected dependencies.
    """

    assert import_service.loader is mock_loader
    assert import_service.validator is mock_validator
    assert import_service.transformer is mock_transformer
    assert (
        import_service.market_data_service
        is mock_market_data_service
    )


def test_import_statistics_creation() -> None:
    """
    Verify ImportStatistics default values.
    """

    stats = ImportStatistics()

    assert stats.files_processed == 0
    assert stats.files_failed == 0
    assert stats.records_imported == 0
    assert stats.records_skipped == 0
from pathlib import Path


# ----------------------------------------------------------------------
# import_file()
# ----------------------------------------------------------------------


def test_import_file_success(
    import_service: ImportService,
    mock_loader: Mock,
    mock_validator: Mock,
    mock_transformer: Mock,
    mock_market_data_service: Mock,
) -> None:
    """
    Verify the complete import pipeline executes successfully.
    """

    dataframe = Mock(name="dataframe")
    transformed_dataframe = Mock(name="transformed_dataframe")

    mock_loader.load.return_value = dataframe
    mock_transformer.transform.return_value = transformed_dataframe
    mock_market_data_service.import_market_data.return_value = 125

    imported = import_service.import_file("SBIN.csv")

    assert imported == 125

    mock_loader.load.assert_called_once_with("SBIN.csv")

    mock_validator.validate.assert_called_once_with(dataframe)

    mock_transformer.transform.assert_called_once_with(dataframe)

    mock_market_data_service.import_market_data.assert_called_once_with(
        transformed_dataframe
    )


def test_import_file_validation_failure(
    import_service: ImportService,
    mock_loader: Mock,
    mock_validator: Mock,
) -> None:
    """
    Validation exceptions should propagate.
    """

    dataframe = Mock()

    mock_loader.load.return_value = dataframe

    mock_validator.validate.side_effect = ValueError(
        "Invalid CSV"
    )

    with pytest.raises(ValueError):
        import_service.import_file("invalid.csv")


# ----------------------------------------------------------------------
# import_directory()
# ----------------------------------------------------------------------


def test_import_directory_missing_directory(
    import_service: ImportService,
    tmp_path: Path,
) -> None:
    """
    Non-existent directory should raise FileNotFoundError.
    """

    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        import_service.import_directory(str(missing))


def test_import_directory_empty(
    import_service: ImportService,
    tmp_path: Path,
) -> None:
    """
    Empty directory should produce empty statistics.
    """

    stats = import_service.import_directory(str(tmp_path))

    assert stats.files_processed == 0
    assert stats.files_failed == 0
    assert stats.records_imported == 0
    assert stats.records_skipped == 0


def test_import_directory_multiple_files(
    import_service: ImportService,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """
    Every CSV file should be processed exactly once.
    """

    (tmp_path / "SBIN.csv").touch()
    (tmp_path / "TCS.csv").touch()
    (tmp_path / "INFY.csv").touch()

    imported = {
        "SBIN.csv": 100,
        "TCS.csv": 200,
        "INFY.csv": 300,
    }

    def fake_import(file_path: str) -> int:
        return imported[Path(file_path).name]

    monkeypatch.setattr(
        import_service,
        "import_file",
        fake_import,
    )

    stats = import_service.import_directory(
        str(tmp_path)
    )

    assert stats.files_processed == 3
    assert stats.files_failed == 0
    assert stats.records_imported == 600


def test_import_directory_partial_failure(
    import_service: ImportService,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """
    Failed files should not stop remaining imports.
    """

    (tmp_path / "A.csv").touch()
    (tmp_path / "B.csv").touch()
    (tmp_path / "C.csv").touch()

    def fake_import(file_path: str) -> int:

        filename = Path(file_path).name

        if filename == "B.csv":
            raise RuntimeError("Import failed")

        return 50

    monkeypatch.setattr(
        import_service,
        "import_file",
        fake_import,
    )

    stats = import_service.import_directory(
        str(tmp_path)
    )

    assert stats.files_processed == 2
    assert stats.files_failed == 1
    assert stats.records_imported == 100
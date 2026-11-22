from pathlib import Path

import pytest

from data_engine.pipeline.universe_master_pipeline import (
    UniverseMasterPipeline,
)
from database.unit_of_work import UnitOfWork
from database.models.symbol import Symbol


def _create_symbol(uow: UnitOfWork, code: str) -> Symbol:
    symbol = Symbol(
        symbol_code=code,
        symbol_name=f"Test {code}",
        exchange="NSE",
        instrument_type="EQUITY",
        is_active=True,
    )

    uow.symbols.add(symbol)
    uow.commit()

    return symbol


def _write_csv(
    path: Path,
    rows: str,
) -> Path:
    content = (
        "universe_code,universe_name,universe_type,"
        "provider,symbol_code,effective_from,effective_to\n"
        + rows
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path


def test_pipeline_imports_valid_universe_csv(
    db_session,
    tmp_path,
):
    uow = UnitOfWork()

    try:
        _create_symbol(uow, "PIPEIMP1")

        file_path = _write_csv(
            tmp_path / "universe.csv",
            (
                "TEST500,Test Universe 500,INDEX,"
                "TEST,PIPEIMP1,2026-01-01,\n"
            ),
        )

        pipeline = UniverseMasterPipeline()
        result = pipeline.import_csv(file_path)

        assert result.success is True
        assert result.rows_read == 1
        assert result.rows_imported == 1
        assert result.rows_failed == 0

        universe = uow.universes.get_by_universe_code(
            "TEST500"
        )

        assert universe is not None

    finally:
        uow.rollback()
        uow.close()


def test_pipeline_reimport_is_idempotent(
    db_session,
    tmp_path,
):
    uow = UnitOfWork()

    try:
        _create_symbol(uow, "PIPEIMP2")

        file_path = _write_csv(
            tmp_path / "universe.csv",
            (
                "TEST500,Test Universe 500,INDEX,"
                "TEST,PIPEIMP2,2026-01-01,\n"
            ),
        )

        pipeline = UniverseMasterPipeline()

        first = pipeline.import_csv(file_path)
        second = pipeline.import_csv(file_path)

        assert first.success is True
        assert first.rows_imported == 1

        assert second.success is True
        assert second.rows_imported == 0
        assert second.rows_failed == 0

    finally:
        uow.rollback()
        uow.close()


def test_pipeline_rejects_invalid_csv(
    db_session,
    tmp_path,
):
    file_path = tmp_path / "invalid.csv"

    file_path.write_text(
        "symbol_code,effective_from\n"
        "PIPEIMP3,2026-01-01\n",
        encoding="utf-8",
    )

    pipeline = UniverseMasterPipeline()
    result = pipeline.import_csv(file_path)

    assert result.success is False
    assert result.rows_read == 1
    assert result.rows_imported == 0
    assert result.rows_failed == 1
    assert result.message == "Universe Master validation failed."


def test_pipeline_rejects_unknown_symbol(
    db_session,
    tmp_path,
):
    file_path = _write_csv(
        tmp_path / "unknown.csv",
        (
            "TEST500,Test Universe 500,INDEX,"
            "TEST,DOES_NOT_EXIST,2026-01-01,\n"
        ),
    )

    pipeline = UniverseMasterPipeline()
    result = pipeline.import_csv(file_path)

    assert result.success is False
    assert result.rows_read == 1
    assert result.rows_imported == 0
    assert result.rows_failed == 1
    assert result.message == "Universe Master database import failed."
    assert "Unknown symbol_code" in (result.exception or "")


def test_pipeline_imports_multiple_memberships(
    db_session,
    tmp_path,
):
    uow = UnitOfWork()

    try:
        _create_symbol(uow, "PIPEIMP4")
        _create_symbol(uow, "PIPEIMP5")

        file_path = _write_csv(
            tmp_path / "universe.csv",
            (
                "TEST500,Test Universe 500,INDEX,"
                "TEST,PIPEIMP4,2026-01-01,\n"
                "TEST500,Test Universe 500,INDEX,"
                "TEST,PIPEIMP5,2026-01-01,\n"
            ),
        )

        pipeline = UniverseMasterPipeline()
        result = pipeline.import_csv(file_path)

        assert result.success is True
        assert result.rows_read == 2
        assert result.rows_imported == 2
        assert result.rows_failed == 0

    finally:
        uow.rollback()
        uow.close()


def test_pipeline_selects_latest_csv(
    db_session,
    tmp_path,
):
    uow = UnitOfWork()

    try:
        _create_symbol(uow, "PIPEIMP6")

        old_file = _write_csv(
            tmp_path / "old.csv",
            (
                "TESTOLD,Test Old Universe,INDEX,"
                "TEST,PIPEIMP6,2026-01-01,\n"
            ),
        )

        new_file = _write_csv(
            tmp_path / "new.csv",
            (
                "TESTNEW,Test New Universe,INDEX,"
                "TEST,PIPEIMP6,2026-01-01,\n"
            ),
        )

        import os
        import time

        old_time = time.time() - 100

        os.utime(
            old_file,
            (old_time, old_time),
        )

        pipeline = UniverseMasterPipeline()
        result = pipeline.import_latest_csv(tmp_path)

        assert result.success is True
        assert result.file_name == "new.csv"

    finally:
        uow.rollback()
        uow.close()


def test_pipeline_latest_csv_directory_not_found(
    db_session,
    tmp_path,
):
    pipeline = UniverseMasterPipeline()

    result = pipeline.import_latest_csv(
        tmp_path / "does_not_exist"
    )

    assert result.success is False
    assert result.message == "Universe Master directory not found."


def test_pipeline_latest_csv_when_no_files_exist(
    db_session,
    tmp_path,
):
    pipeline = UniverseMasterPipeline()

    result = pipeline.import_latest_csv(tmp_path)

    assert result.success is False
    assert result.message == "No Universe Master CSV files found."

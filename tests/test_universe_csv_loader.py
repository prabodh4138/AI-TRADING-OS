from pathlib import Path

import pandas as pd
import pytest

from data_engine.loader.universe_csv_loader import UniverseCSVLoader


def _write_csv(
    path: Path,
    content: str,
    encoding: str = "utf-8",
) -> Path:
    path.write_text(
        content,
        encoding=encoding,
    )
    return path


def test_load_valid_csv(tmp_path):
    file_path = _write_csv(
        tmp_path / "universe.csv",
        (
            "universe_code,universe_name,universe_type,"
            "provider,symbol_code,effective_from,effective_to\n"
            "NIFTY500,NIFTY 500,INDEX,NSE,RELIANCE,"
            "2026-01-01,\n"
        ),
    )

    loader = UniverseCSVLoader()

    dataframe = loader.load(file_path)

    assert isinstance(dataframe, pd.DataFrame)
    assert len(dataframe) == 1
    assert list(dataframe.columns) == [
        "universe_code",
        "universe_name",
        "universe_type",
        "provider",
        "symbol_code",
        "effective_from",
        "effective_to",
    ]


def test_load_preserves_empty_values_as_empty_strings(tmp_path):
    file_path = _write_csv(
        tmp_path / "universe.csv",
        (
            "universe_code,universe_name,universe_type,"
            "provider,symbol_code,effective_from,effective_to\n"
            "NIFTY500,NIFTY 500,INDEX,NSE,RELIANCE,"
            "2026-01-01,\n"
        ),
    )

    dataframe = UniverseCSVLoader().load(file_path)

    assert dataframe.loc[0, "effective_to"] == ""


def test_load_normalizes_column_whitespace(tmp_path):
    file_path = _write_csv(
        tmp_path / "universe.csv",
        (
            " universe_code , universe_name ,symbol_code \n"
            "NIFTY500,NIFTY 500,RELIANCE\n"
        ),
    )

    dataframe = UniverseCSVLoader().load(file_path)

    assert list(dataframe.columns) == [
        "universe_code",
        "universe_name",
        "symbol_code",
    ]


def test_load_missing_file():
    loader = UniverseCSVLoader()

    with pytest.raises(
        FileNotFoundError,
        match="CSV file not found",
    ):
        loader.load(
            Path("does_not_exist_universe.csv")
        )


def test_load_requires_path_object(tmp_path):
    file_path = tmp_path / "universe.csv"

    _write_csv(
        file_path,
        "universe_code\nNIFTY500\n",
    )

    loader = UniverseCSVLoader()

    with pytest.raises(
        TypeError,
        match="pathlib.Path",
    ):
        loader.load(str(file_path))


def test_load_rejects_directory(tmp_path):
    loader = UniverseCSVLoader()

    with pytest.raises(
        FileNotFoundError,
        match="Invalid CSV file",
    ):
        loader.load(tmp_path)


def test_load_empty_csv(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8")

    loader = UniverseCSVLoader()

    with pytest.raises(
        ValueError,
        match="CSV is empty",
    ):
        loader.load(file_path)


def test_load_header_only_csv(tmp_path):
    file_path = _write_csv(
        tmp_path / "header_only.csv",
        (
            "universe_code,universe_name,symbol_code\n"
        ),
    )

    loader = UniverseCSVLoader()

    with pytest.raises(
        ValueError,
        match="DataFrame is empty",
    ):
        loader.load(file_path)


def test_load_latin1_csv(tmp_path):
    file_path = tmp_path / "universe_latin1.csv"

    file_path.write_bytes(
        (
            "universe_code,universe_name,symbol_code\n"
            "TEST,Indéx,RELIANCE\n"
        ).encode("latin-1")
    )

    loader = UniverseCSVLoader()

    dataframe = loader.load(file_path)

    assert len(dataframe) == 1
    assert dataframe.loc[0, "universe_name"] == "Indéx"


def test_preview_returns_requested_rows(tmp_path):
    file_path = _write_csv(
        tmp_path / "universe.csv",
        (
            "universe_code,symbol_code\n"
            "NIFTY500,RELIANCE\n"
            "NIFTY500,TCS\n"
            "NIFTY500,INFY\n"
        ),
    )

    loader = UniverseCSVLoader()

    dataframe = loader.load(file_path)
    preview = loader.preview(dataframe, rows=2)

    assert len(preview) == 2
    assert preview.iloc[0]["symbol_code"] == "RELIANCE"


def test_preview_rejects_invalid_dataframe():
    loader = UniverseCSVLoader()

    with pytest.raises(
        TypeError,
        match="pandas.DataFrame",
    ):
        loader.preview("invalid")


def test_preview_rejects_negative_rows(tmp_path):
    file_path = _write_csv(
        tmp_path / "universe.csv",
        "universe_code,symbol_code\nNIFTY500,RELIANCE\n",
    )

    loader = UniverseCSVLoader()
    dataframe = loader.load(file_path)

    with pytest.raises(
        ValueError,
        match="greater than or equal to zero",
    ):
        loader.preview(dataframe, rows=-1)

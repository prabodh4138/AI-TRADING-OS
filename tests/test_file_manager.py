from pathlib import Path

from data_engine.storage.file_manager import FileManager


def test_build_filename():
    fm = FileManager(Path("downloads"))

    name = fm.build_filename(
        prefix="sec_bhavdata_full_",
        extension="csv",
        identifier="01012025",
    )

    assert (
        name ==
        "sec_bhavdata_full_01012025.csv"
    )


def test_save_and_read(tmp_path):
    fm = FileManager(tmp_path)

    path = fm.build_path("sample.txt")

    fm.save_text(
        path,
        "Hello AI Trading OS",
    )

    assert fm.exists(path)

    text = fm.read_text(path)

    assert text == "Hello AI Trading OS"


def test_delete(tmp_path):
    fm = FileManager(tmp_path)

    path = fm.build_path("delete.txt")

    fm.save_text(path, "Delete Me")

    assert fm.delete(path)

    assert not fm.exists(path)
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from scripts.convert_matrix_csv import convert_csv_to_matrix, ConversionError


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_numeric_only_csv_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,2\n3,4\n")
    m = convert_csv_to_matrix(p)
    assert m.shape == (2, 2)
    assert m.dtype == np.float64
    assert np.allclose(m, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_header_and_id_column_by_name(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "id,a,b\nA,1,2\nB,3,4\n")
    m = convert_csv_to_matrix(p, has_header=True, id_col="id")
    assert np.allclose(m, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_id_column_by_index(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "A,1,2\nB,3,4\n")
    m = convert_csv_to_matrix(p, has_header=False, id_col="0")
    assert np.allclose(m, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_non_rectangular_rejected(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,2\n3\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p)


def test_non_numeric_rejected(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,2\n3,x\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p)


def test_empty_cell_rejected_by_default(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,\n3,4\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p)


def test_empty_cell_can_be_filled(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,\n3,4\n")
    m = convert_csv_to_matrix(p, fill_empty=0.0)
    assert np.allclose(m, np.array([[1.0, 0.0], [3.0, 4.0]]))


def test_blank_lines_skipped(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "\n1,2\n\n3,4\n\n")
    m = convert_csv_to_matrix(p)
    assert m.shape == (2, 2)


def test_all_empty_cells_row_rejected(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", ",,\n1,2,3\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p)


def test_fill_empty_rejects_nan(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,\n3,4\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p, fill_empty=float('nan'))


def test_fill_empty_rejects_inf_even_if_not_used(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "1,2\n3,4\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p, fill_empty=float('inf'))


def test_blank_lines_skipped_with_crlf_and_cr(tmp_path: Path) -> None:
    # CRLF
    p = _write(tmp_path, "m.csv", "\r\n1,2\r\n\r\n3,4\r\n")
    m = convert_csv_to_matrix(p)
    assert m.shape == (2, 2)

    # Bare CR (rare, but seen in legacy exports)
    p2 = tmp_path / "m_cr.csv"
    p2.write_bytes(b"\r1,2\r\r3,4\r")
    m2 = convert_csv_to_matrix(p2)
    assert m2.shape == (2, 2)


def test_oserror_wrapped_as_conversion_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(missing)


def test_csv_error_wrapped_as_conversion_error(tmp_path: Path, monkeypatch) -> None:
    import scripts.convert_matrix_csv as mod

    def boom(*args, **kwargs):
        raise mod.csv.Error("bad csv")

    monkeypatch.setattr(mod, "read_csv_rows", boom)
    with pytest.raises(ConversionError):
        mod.convert_csv_to_matrix(tmp_path / "x.csv")


def test_header_only_rejected(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.csv", "a,b\n")
    with pytest.raises(ConversionError):
        convert_csv_to_matrix(p, has_header=True)

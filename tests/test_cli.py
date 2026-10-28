"""Regression tests for the public ELECTRE III command-line workflow."""
import json
import sys

import numpy as np

from electre3.cli import main


def _criteria_file(tmp_path):
    path = tmp_path / "criteria.json"
    path.write_text(json.dumps([{
        "name": "benefit", "weight": 1.0, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True,
    }]), encoding="utf-8")
    return path


def test_cli_saves_ranking_with_existing_flags(tmp_path, monkeypatch, capsys):
    matrix = tmp_path / "matrix.npy"
    output = tmp_path / "ranking.npy"
    np.save(matrix, np.array([[0.1], [0.9]]))
    monkeypatch.setattr(sys, "argv", ["electre3", str(matrix), str(_criteria_file(tmp_path)), "-y", "-q", "-o", str(output)])
    assert main() == 0
    assert capsys.readouterr().out == ""
    assert np.array_equal(np.load(output), np.array([1, 0]))


def test_cli_reports_load_errors_to_stderr(tmp_path, monkeypatch, capsys):
    missing = tmp_path / "missing.npy"
    monkeypatch.setattr(sys, "argv", ["electre3", str(missing), str(_criteria_file(tmp_path)), "-y"])
    assert main() == 1
    assert "Error loading input:" in capsys.readouterr().err


def test_cli_aborts_on_eof_confirmation(tmp_path, monkeypatch, capsys):
    matrix = tmp_path / "matrix.npy"
    np.save(matrix, np.array([[0.1], [0.9]]))
    monkeypatch.setattr(sys, "argv", ["electre3", str(matrix), str(_criteria_file(tmp_path))])
    monkeypatch.setattr("builtins.input", lambda prompt: (_ for _ in ()).throw(EOFError))
    assert main() == 0
    assert capsys.readouterr().out.endswith("Aborted.\n")

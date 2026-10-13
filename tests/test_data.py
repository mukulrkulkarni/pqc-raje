"""Tests for electre3.data module."""

import numpy as np
import pytest
import tempfile
from pathlib import Path
from electre3.data import load_matrix


class TestLoadMatrix:
    """Tests for matrix loading from various formats."""

    def test_load_npy(self, tmp_path):
        """Should load .npy files."""
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
        path = tmp_path / "test.npy"
        np.save(path, matrix)

        loaded = load_matrix(path)
        assert np.allclose(loaded, matrix)
        assert loaded.dtype == np.float64

    def test_load_npz(self, tmp_path):
        """Should load .npz files."""
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
        path = tmp_path / "test.npz"
        np.savez(path, data=matrix)

        loaded = load_matrix(path)
        assert np.allclose(loaded, matrix)

    def test_load_csv(self, tmp_path):
        """Should load .csv files."""
        path = tmp_path / "test.csv"
        path.write_text("1.0,2.0\n3.0,4.0\n")

        loaded = load_matrix(path)
        expected = np.array([[1.0, 2.0], [3.0, 4.0]])
        assert np.allclose(loaded, expected)

    def test_load_string_path(self, tmp_path):
        """Should accept string path."""
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
        path = tmp_path / "test.npy"
        np.save(path, matrix)

        loaded = load_matrix(str(path))
        assert np.allclose(loaded, matrix)

    def test_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_matrix(tmp_path / "nonexistent.npy")

    def test_unsupported_format(self, tmp_path):
        """Should raise ValueError for unsupported formats."""
        path = tmp_path / "test.xyz"
        path.write_text("data")

        with pytest.raises(ValueError, match="Unsupported"):
            load_matrix(path)

    def test_converts_to_float64(self, tmp_path):
        """Should convert to float64."""
        matrix = np.array([[1, 2], [3, 4]], dtype=np.int32)
        path = tmp_path / "test.npy"
        np.save(path, matrix)

        loaded = load_matrix(path)
        assert loaded.dtype == np.float64

    def test_case_insensitive_extension(self, tmp_path):
        """Should handle uppercase extensions."""
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
        # np.save adds .npy, so save to lowercase then rename
        path_lower = tmp_path / "test.npy"
        np.save(path_lower, matrix)
        path_upper = tmp_path / "test.NPY"
        path_lower.rename(path_upper)

        loaded = load_matrix(path_upper)
        assert np.allclose(loaded, matrix)

    def test_large_matrix(self, tmp_path):
        """Should handle large matrices."""
        matrix = np.random.rand(1000, 50)
        path = tmp_path / "large.npy"
        np.save(path, matrix)

        loaded = load_matrix(path)
        assert loaded.shape == (1000, 50)
        assert np.allclose(loaded, matrix)

    def test_preserves_values(self, tmp_path):
        """Should preserve exact values."""
        matrix = np.array([[1.23456789, 9.87654321], [0.00000001, 99999999.9]])
        path = tmp_path / "test.npy"
        np.save(path, matrix)

        loaded = load_matrix(path)
        assert np.allclose(loaded, matrix, rtol=1e-15)

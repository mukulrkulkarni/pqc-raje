"""Tests for security service functions."""

import pytest
from app.services.security import (
    validate_upload_id,
    validate_criteria_json,
    register_upload,
    get_upload_path,
)
from pathlib import Path


class TestValidateUploadId:
    """Tests for upload ID validation."""

    def test_valid_alphanumeric(self):
        """Alphanumeric IDs should be valid."""
        assert validate_upload_id("abc123")
        assert validate_upload_id("ABC123")
        assert validate_upload_id("AbC123xYz")

    def test_valid_with_hyphens(self):
        """IDs with hyphens should be valid."""
        assert validate_upload_id("abc-123")
        assert validate_upload_id("test-upload-id")

    def test_invalid_with_dots(self):
        """IDs with dots should be invalid (path traversal risk)."""
        assert not validate_upload_id("../etc/passwd")
        assert not validate_upload_id("test.txt")

    def test_invalid_with_slashes(self):
        """IDs with slashes should be invalid."""
        assert not validate_upload_id("path/to/file")
        assert not validate_upload_id("path\\to\\file")

    def test_invalid_with_spaces(self):
        """IDs with spaces should be invalid."""
        assert not validate_upload_id("test upload")

    def test_invalid_empty(self):
        """Empty ID should be invalid."""
        assert not validate_upload_id("")

    def test_invalid_special_chars(self):
        """IDs with special characters should be invalid."""
        assert not validate_upload_id("test@upload")
        assert not validate_upload_id("test#upload")
        assert not validate_upload_id("test$upload")


class TestValidateCriteriaJson:
    """Tests for criteria JSON validation."""

    def test_valid_criteria(self):
        """Valid criteria should return None."""
        criteria = [
            {"name": "A", "weight": 1, "q": 1, "p": 2, "v": 3},
            {"name": "B", "weight": 2, "q": 2, "p": 4, "v": 6},
        ]
        assert validate_criteria_json(criteria) is None

    def test_not_a_list(self):
        """Non-list should return error."""
        error = validate_criteria_json({"name": "A", "weight": 1})
        assert error is not None
        assert "list" in error

    def test_empty_list(self):
        """Empty list should return error."""
        error = validate_criteria_json([])
        assert error is not None
        assert "empty" in error

    def test_missing_weight(self):
        """Missing weight should return error."""
        criteria = [{"name": "A", "q": 1, "p": 2, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "weight" in error

    def test_missing_q(self):
        """Missing q should return error."""
        criteria = [{"name": "A", "weight": 1, "p": 2, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "q" in error

    def test_missing_p(self):
        """Missing p should return error."""
        criteria = [{"name": "A", "weight": 1, "q": 1, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "p" in error

    def test_missing_v(self):
        """Missing v should return error."""
        criteria = [{"name": "A", "weight": 1, "q": 1, "p": 2}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "v" in error

    def test_negative_q(self):
        """Negative q should return error."""
        criteria = [{"weight": 1, "q": -1, "p": 2, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "q" in error

    def test_p_less_than_q(self):
        """p < q should return error."""
        criteria = [{"weight": 1, "q": 5, "p": 2, "v": 10}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "p" in error

    def test_v_less_than_p(self):
        """v < p should return error."""
        criteria = [{"weight": 1, "q": 1, "p": 5, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "v" in error

    def test_zero_weight(self):
        """Zero weight should return error."""
        criteria = [{"weight": 0, "q": 1, "p": 2, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "weight" in error

    def test_negative_weight(self):
        """Negative weight should return error."""
        criteria = [{"weight": -1, "q": 1, "p": 2, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "weight" in error

    def test_non_numeric_weight(self):
        """Non-numeric weight should return error."""
        criteria = [{"weight": "high", "q": 1, "p": 2, "v": 3}]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "numeric" in error

    def test_criterion_not_dict(self):
        """Non-dict criterion should return error."""
        criteria = ["not a dict"]
        error = validate_criteria_json(criteria)
        assert error is not None
        assert "object" in error

    def test_equal_thresholds_valid(self):
        """Equal thresholds (q=p=v) should be valid."""
        criteria = [{"weight": 1, "q": 5, "p": 5, "v": 5}]
        assert validate_criteria_json(criteria) is None


class TestUploadRegistry:
    """Tests for upload registry functions."""

    def test_register_and_retrieve(self, tmp_path):
        """Should be able to register and retrieve."""
        path = tmp_path / "test.npy"
        path.touch()
        register_upload("registry-test", path)
        assert get_upload_path("registry-test") == path

    def test_unregistered_returns_none(self):
        """Unregistered ID should return None."""
        assert get_upload_path("never-registered-xyz") is None

    def test_overwrite_registration(self, tmp_path):
        """Should allow overwriting registration."""
        path1 = tmp_path / "test1.npy"
        path2 = tmp_path / "test2.npy"
        path1.touch()
        path2.touch()

        register_upload("overwrite-test", path1)
        register_upload("overwrite-test", path2)
        assert get_upload_path("overwrite-test") == path2

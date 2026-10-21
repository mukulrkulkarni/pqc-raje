"""Tests for security service functions."""

from pathlib import Path

import pytest

from app.services.security import (
    get_upload_path,
    register_upload,
    validate_criteria_json,
    validate_upload_id,
)


def _criterion(**changes):
    value = {"name": "A", "weight": 1.0, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True}
    value.update(changes)
    return value


class TestValidateUploadId:
    @pytest.mark.parametrize("upload_id", ["abc123", "ABC123", "abc-123"])
    def test_accepts_allowed_ids(self, upload_id):
        assert validate_upload_id(upload_id)

    @pytest.mark.parametrize("upload_id", ["../etc/passwd", "test.txt", "path/to/file", "path\\to\\file", "test upload", "", "test@upload"])
    def test_rejects_path_and_special_characters(self, upload_id):
        assert not validate_upload_id(upload_id)


class TestValidateCriteriaJson:
    def test_accepts_complete_shared_contract_criteria(self):
        criteria = [_criterion(name="A", weight=0.4), _criterion(name="B", weight=0.6, maximize=False)]
        assert validate_criteria_json(criteria) is None

    @pytest.mark.parametrize(("criteria", "message"), [
        ({"name": "A"}, "list"),
        ([], "1 through 8"),
        ([_criterion(name="")], "non-empty"),
        ([{key: value for key, value in _criterion().items() if key != "maximize"}], "maximize"),
        ([_criterion(weight=0.9)], "sum to 1"),
        ([_criterion(weight="high")], "finite number"),
        ([_criterion(q=-0.1)], "q must be >= 0"),
        ([_criterion(q=0.3, p=0.2)], "p must be >= q"),
        ([_criterion(p=0.4, v=0.3)], "v must be >= p"),
        (["not an object"], "object"),
    ])
    def test_returns_shared_contract_errors(self, criteria, message):
        error = validate_criteria_json(criteria)
        assert error is not None
        assert message in error

    def test_accepts_equal_thresholds(self):
        assert validate_criteria_json([_criterion(q=0.2, p=0.2, v=0.2)]) is None


class TestUploadRegistry:
    def test_register_and_retrieve(self, tmp_path):
        path = tmp_path / "test.npy"
        path.touch()
        register_upload("registry-test", path)
        assert get_upload_path("registry-test") == path

    def test_unregistered_returns_none(self):
        assert get_upload_path("never-registered-xyz") is None

    def test_overwrites_registration(self, tmp_path):
        first = tmp_path / "first.npy"
        second = tmp_path / "second.npy"
        first.touch()
        second.touch()
        register_upload("overwrite-test", first)
        register_upload("overwrite-test", second)
        assert get_upload_path("overwrite-test") == second

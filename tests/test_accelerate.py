"""Tests for optional Numba acceleration."""

import pytest
from electre3.accelerate import HAS_NUMBA, _concordance_numba, _discordance_numba


class TestAccelerateModule:
    """Tests for accelerate module."""

    def test_has_numba_is_bool(self):
        """HAS_NUMBA should be a boolean."""
        assert isinstance(HAS_NUMBA, bool)

    def test_concordance_exists_or_none(self):
        """_concordance_numba should be callable or None."""
        if HAS_NUMBA:
            assert callable(_concordance_numba)
        else:
            assert _concordance_numba is None

    def test_discordance_exists_or_none(self):
        """_discordance_numba should be callable or None."""
        if HAS_NUMBA:
            assert callable(_discordance_numba)
        else:
            assert _discordance_numba is None

    @pytest.mark.skipif(not HAS_NUMBA, reason="Numba not installed")
    def test_numba_concordance_basic(self):
        """Basic concordance computation with Numba."""
        import numpy as np
        diff = np.array([[[5.0, -4.0]]], dtype=np.float64)
        q = np.array([3.0, 3.0], dtype=np.float64)
        p = np.array([5.0, 5.0], dtype=np.float64)
        out = np.zeros_like(diff)
        _concordance_numba(diff, q, p, out)
        assert out[0, 0, 0] == 1.0  # diff=5 >= -q=-3
        assert 0 < out[0, 0, 1] < 1  # interpolated

    @pytest.mark.skipif(not HAS_NUMBA, reason="Numba not installed")
    def test_numba_discordance_basic(self):
        """Basic discordance computation with Numba."""
        import numpy as np
        diff = np.array([[[0.0, -15.0]]], dtype=np.float64)
        p = np.array([5.0, 5.0], dtype=np.float64)
        v = np.array([10.0, 10.0], dtype=np.float64)
        out = np.zeros_like(diff)
        _discordance_numba(diff, p, v, out)
        assert out[0, 0, 0] == 0.0  # diff=0 >= -p=-5
        assert out[0, 0, 1] == 1.0  # diff=-15 <= -v=-10

"""Dummy plugin test in tests's root folder."""

from .test_base import TestBase


class TestRoot(TestBase):
    """Test in root folder."""

    def test_true(self):
        """Test with input param True"""
        self.assertTrue(self._run_dummy(True))

    def test_false(self):
        """Test with input param False"""
        self.assertFalse(self._run_dummy(False))

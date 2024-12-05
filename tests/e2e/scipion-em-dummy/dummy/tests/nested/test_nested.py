"""Dummy plugin test inside a nested test folder."""

from ..test_base import TestBase


class TestNested(TestBase):
    """Test in nested folder."""

    def test_true(self):
        """Test with input param True"""
        self.assertTrue(self._run_dummy(True))

    def test_false(self):
        """Test with input param False"""
        self.assertFalse(self._run_dummy(False))

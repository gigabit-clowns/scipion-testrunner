from ..test_base import TestBase

class TestNested(TestBase):
  def test_true(self):
    self.assertTrue(self._run_dummy(True))

  def test_false(self):
    self.assertFalse(self._run_dummy(False))

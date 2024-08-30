from pyworkflow.tests import BaseTest, setupTestProject

from ...protocols import ProtDummy

class TestNested(BaseTest):
  @classmethod
  def setUpClass(cls):
    setupTestProject(cls)
  
  def __run_dummy(self, status: bool) -> bool:
    prot_dummy = self.newProtocol(ProtDummy, {"inputStatus": status})
    self.launchProtocol(prot_dummy)
    return getattr(prot_dummy, prot_dummy._OUTNAME)

  def test_true(self):
    self.assertIsTrue(self.__run_dummy(True))

  def test_false(self):
    self.assertIsTrue(self.__run_dummy(False))

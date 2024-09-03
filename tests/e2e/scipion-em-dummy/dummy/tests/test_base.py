from pyworkflow.tests import BaseTest, setupTestProject

from ..protocols import ProtDummy

class TestBase(BaseTest):
  @classmethod
  def setUpClass(cls):
    setupTestProject(cls)
  
  def _run_dummy(self, status: bool) -> bool:
    prot_dummy = self.newProtocol(ProtDummy, inputStatus=status)
    self.launchProtocol(prot_dummy)
    return getattr(prot_dummy, prot_dummy._OUTNAME)

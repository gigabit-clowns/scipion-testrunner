"""Test template for dummy plugin."""

from pyworkflow.tests import BaseTest, setupTestProject

from ..protocols import ProtDummy


class TestBase(BaseTest):
    """Test template."""

    @classmethod
    def setUpClass(cls):
        """Configuration of the test project."""
        setupTestProject(cls)

    def _run_dummy(self, status: bool) -> bool:
        """Run dummy protocol."""
        prot_dummy = self.newProtocol(ProtDummy, inputStatus=status)
        self.launchProtocol(prot_dummy)
        return getattr(prot_dummy, prot_dummy.OUTNAME)

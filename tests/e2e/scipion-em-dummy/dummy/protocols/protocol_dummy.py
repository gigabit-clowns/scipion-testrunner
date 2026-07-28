"""Dummy protocol for testing."""

from typing import ClassVar

from pwem.protocols import EMProtocol
from pyworkflow.protocol import Boolean, params
from pyworkflow.utils import Message


class ProtDummy(EMProtocol):
    """
    Dummy protocol to perform E2E testing.
    """

    _label = "Dummy"
    OUTNAME = "outputStatus"
    _possibleOutputs: ClassVar = {OUTNAME: bool}

    def _defineParams(self, form):
        """
        Defines parameters for the protocol
        """
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam(
            "inputStatus",
            params.BooleanParam,
            default=True,
            label="Input status to be returned: ",
            help="The input status received in this param is the same one that will be returned by the protocol.",
        )

    def _insertAllSteps(self):
        """
        Insert processing steps for the protocol
        """
        self._insertFunctionStep("inputToOutputStep")

    def inputToOutputStep(self):
        """
        Returns the form input as output
        """
        self._defineOutputs(**{self.OUTNAME: Boolean(self.inputStatus.get())})

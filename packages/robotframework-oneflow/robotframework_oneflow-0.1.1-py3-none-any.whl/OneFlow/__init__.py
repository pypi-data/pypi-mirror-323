from .listener import OneFlowSuite


class OneFlow:
    """Treat a whole test suite as a one flow. If any of the test case fail, the rest are skipped."""

    ROBOT_LIBRARY_SCOPE = "SUITE"
    ROBOT_LIBRARY_LISTENER = OneFlowSuite()

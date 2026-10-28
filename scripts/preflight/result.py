"""Preflight result value."""


class CheckResult:
    """Store a check outcome and messages."""

    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.messages: list[str] = []

    def fail(self, message: str) -> None:
        self.passed = False
        self.messages.append(f"FAIL: {message}")

    def info(self, message: str) -> None:
        self.messages.append(f"INFO: {message}")

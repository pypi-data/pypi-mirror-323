from .severity import Severity


class CheckException(Exception):
    """CheckException is the basic check exception."""
    def __init__(self, msg: str, severity: Severity = Severity.MEDIUM):
        assert msg, 'CheckException message must not be empty'
        self.severity = severity
        super().__init__(msg)

    def to_dict(self):
        return {
            "message": self.__str__(),
            "severity": self.severity.value
        }

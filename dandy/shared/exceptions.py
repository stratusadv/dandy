class DandyError(Exception):
    pass


class DandyCriticalError(DandyError):
    pass


class DandyRecoverableError(DandyError):
    pass


class FileCriticalError(DandyCriticalError):
    pass


class FileRecoverableError(DandyRecoverableError):
    pass


class RunStoppedError(DandyRecoverableError):
    """Raised at a stop checkpoint when the user asked to stop a running turn.

    Lives in the shared layer so application, infrastructure, and interfaces
    can all raise and catch it without cross-layer imports.
    """

    pass

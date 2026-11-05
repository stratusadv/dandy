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


# The message every stop checkpoint raises with, so a stopped run reads the
# same way no matter which layer noticed the signal.
RUN_STOPPED_MESSAGE = 'Run stopped by user.'

class DandyError(Exception):
    pass


class DandyConfigurationError(DandyError):
    pass


class DandyUsageError(DandyError):
    pass


class DandyExternalError(DandyError):
    pass


class DandyFlowError(DandyError):
    pass


class FileUsageError(DandyUsageError):
    pass


class FileExternalError(DandyExternalError):
    pass


class RunStoppedError(DandyFlowError):
    """Raised at a stop checkpoint when the user asked to stop a running turn.

    Lives in the shared layer so application, infrastructure, and interfaces
    can all raise and catch it without cross-layer imports.
    """

    pass


# The message every stop checkpoint raises with, so a stopped run reads the
# same way no matter which layer noticed the signal.
RUN_STOPPED_MESSAGE = 'Run stopped by user.'

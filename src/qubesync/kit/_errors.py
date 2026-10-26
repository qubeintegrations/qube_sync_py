"""The errors the kit raises of its own."""
from typing import Optional

from ..errors import QubeSyncError

__all__ = ["CONFIG_FILE", "NotConfigured", "NotReady", "NotConnected", "UnknownOperation"]

# Where an app writes its settings, named in every NotConfigured.
CONFIG_FILE = "quickbooks_desktop/config.py"


class NotConfigured(QubeSyncError, LookupError):
    """A setting the kit needs and your app hasn't written, raised the first time it's needed.
    Its message names the setting and where to write it."""

    def __init__(self, setting, message=None):
        # type: (str, Optional[str]) -> None
        self.setting = setting
        super().__init__(message or "QuBe Sync: %s isn't set yet." % setting)


class NotReady(QubeSyncError):
    """A connection's event came before the row's qube_id was saved (create_connection hadn't
    returned yet, or its save hadn't committed: a simulated connection sends
    connection.connected at once). The job raises it so the queue retries once it's there."""


class NotConnected(QubeSyncError, ValueError):
    """Operation.start was given a connection QuBe Sync hasn't made yet (no qube_id): the
    customer hasn't finished onboarding, or QuBe Sync didn't answer it."""


class UnknownOperation(QubeSyncError, LookupError):
    """A run whose operation none of the operations setting has any more (taken out after it
    started)."""

"""Exception base class, in a module of its own so the webhooks module needs no HTTP client."""


class QubeSyncError(Exception):
    pass

import importlib
import importlib.util

from django.apps import AppConfig
from django.conf import settings

DEFAULT_CONFIG = "quickbooks_desktop.config"


class QubeSyncConfig(AppConfig):
    """qubesync.django in INSTALLED_APPS: the question template, and, once the apps are
    ready, your quickbooks_desktop/config.py imported, so its qubesync.kit.configure(...)
    has run before the first request or job. The QUBESYNC_CONFIG Django setting names
    another module."""

    name = "qubesync.django"
    label = "qubesync"
    verbose_name = "QuBe Sync"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        module = getattr(settings, "QUBESYNC_CONFIG", None)
        if module:
            importlib.import_module(module)
            return
        try:
            found = importlib.util.find_spec(DEFAULT_CONFIG) is not None
        except ImportError:  # no quickbooks_desktop package at all
            found = False
        if found:
            importlib.import_module(DEFAULT_CONFIG)
        # Otherwise the first setting needed raises, naming the file.

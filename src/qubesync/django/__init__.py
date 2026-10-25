"""QuBe Sync's integration kit for Django: an installed app with the routes, the question
template, and Operation and ConnectionEvents bases that save with save(update_fields=...)
and lock the record's row while they apply an event.

    pip install "qubesync[django]>=0.4.0"

    # settings.py
    INSTALLED_APPS += ["qubesync.django"]

    # urls.py
    urlpatterns += [path("", include("qubesync.django.urls"))]

    # quickbooks_desktop/config.py, imported when the app is ready (the QUBESYNC_CONFIG
    # Django setting names another module)
    import qubesync.kit
    qubesync.kit.configure(
        operations={"create_invoice": "quickbooks_desktop.create_invoice.CreateInvoice"},
        connection="quickbooks_desktop.connection.Connection",
        current_account=lambda request: request.user.account,
        authorize_question=lambda request, record, operation: record.account_id == request.user.account_id,
    )

The routes, relative to where urls.py includes them (each named in the qubesync namespace):

    POST quickbooks/connect                        connect   onboarding, behind login_required
    POST webhooks/qube/<operation>/<record id>     webhook   no sign-in, no CSRF (signed)
    POST qube/questions/<operation>/<record id>    answer    behind login_required and CSRF
    GET  qube/questions/<operation>/<record id>/search  search  behind login_required
"""
try:
    import django as _django  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.django needs Django: pip install "qubesync[django]"') from error

from typing import Any, Dict, List

from ..kit import _bases
from ..kit import question_context as _question_context

__all__ = ["Operation", "ConnectionEvents", "question_context", "lock_record"]


def lock_record(record):
    # type: (Any) -> Any
    """record read again with a row lock (select_for_update), inside the transaction the
    caller opened, or record as it is when it isn't a saved Django model."""
    meta = getattr(record, "_meta", None)
    if meta is None or getattr(record, "pk", None) is None:
        return record
    manager = type(record)._base_manager.using(record._state.db)
    return manager.select_for_update().get(pk=record.pk)


def _atomic(record):
    from django.db import DEFAULT_DB_ALIAS, transaction

    state = getattr(record, "_state", None)
    return transaction.atomic(using=getattr(state, "db", None) or DEFAULT_DB_ALIAS)


class Operation(_bases.Operation):
    __doc__ = _bases.Operation.__doc__

    def handle(self, event):
        # type: (Any) -> None
        """Operation.handle, inside a transaction, with the record read again under a row
        lock (lock_record), so two workers never apply one record's events at once and a
        handler that raises leaves the record as it was, for your queue to retry."""
        with _atomic(self.record):
            self.record = self.lock_record(self.record)
            super().handle(event)

    def lock_record(self, record):
        # type: (Any) -> Any
        """The record, locked for the rest of handle's transaction. Override it to lock
        another way, or return record to not lock."""
        return lock_record(record)

    def save_record(self, fields):
        # type: (List[str]) -> None
        """Writes those fields of the record, as Django's models do. Override it to keep
        them elsewhere."""
        self.record.save(update_fields=fields)


class ConnectionEvents(_bases.ConnectionEvents):
    __doc__ = _bases.ConnectionEvents.__doc__

    def handle(self, event):
        # type: (Any) -> None
        """ConnectionEvents.handle, inside a transaction, with the account read again under
        a row lock."""
        with _atomic(self.account):
            self.account = self.lock_record(self.account)
            super().handle(event)

    def lock_record(self, account):
        # type: (Any) -> Any
        return lock_record(account)

    def save_record(self, fields):
        # type: (List[str]) -> None
        """Writes those fields of the account, as Django's models do. Override it to keep
        them elsewhere."""
        self.account.save(update_fields=fields)


def question_context(slug, record):
    # type: (str, Any) -> Dict[str, Any]
    """What the question template reads, for the record's page: the question the run is
    asking about record, if any, and where it's answered. In the page's view:

        context = {"invoice": invoice,
                   **qubesync.django.question_context("create_invoice", invoice)}
        return render(request, "invoice.html", context)

    and in invoice.html, {% include "qubesync/question.html" %}."""
    from django.urls import reverse

    action = reverse("qubesync:answer", args=[slug, record.pk])
    return _question_context(slug, record, action)

"""The kit's tables as Django models: Connection, Run, QuickbooksRecord and Notification, from
qubesync.django's migrations (python manage.py migrate qubesync).

The polymorphic columns (owner_type, record_type) keep your model's label (myapp.Invoice), and
owner_id and record_id are strings, so integer and UUID keys both fit. input, error, question
and links are JSON kept as text (JSONTextField). The 100-character limits keep the composite
keys inside MySQL's 3072-byte limit under utf8mb4.
"""
from django.db import models

from ..kit._models import STATUSES, ConnectionMixin, QuickbooksRecordMixin, RunMixin, family_for
from .fields import JSONTextField
from .store import STORE

__all__ = ["Connection", "Run", "QuickbooksRecord", "Notification"]


class Connection(ConnectionMixin, models.Model):
    __doc__ = ConnectionMixin.__doc__

    _kit_store = STORE

    id = models.BigAutoField(primary_key=True)
    owner_type = models.CharField(max_length=100)
    owner_id = models.CharField(max_length=255)
    qube_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="pending", choices=[(s, s) for s in STATUSES])
    stall_reason = models.CharField(max_length=255, null=True, blank=True)
    revision = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "qubesync"
        db_table = "qube_connections"
        constraints = [models.UniqueConstraint(fields=["qube_id"], name="index_qube_connections_on_qube_id")]
        # Django keeps an index's name to 30 characters, so it's shorter than Rails' own.
        indexes = [models.Index(fields=["owner_type", "owner_id"], name="qube_connections_owner")]

    def __str__(self):
        return "Connection %s (%s)" % (self.pk, self.status)


class Run(RunMixin, models.Model):
    __doc__ = RunMixin.__doc__

    _kit_store = STORE

    id = models.BigAutoField(primary_key=True)
    connection = models.ForeignKey(Connection, on_delete=models.PROTECT, related_name="runs")
    operation = models.CharField(max_length=100)
    record_type = models.CharField(max_length=100)
    record_id = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    qube_run_id = models.CharField(max_length=255, null=True, blank=True)
    input = JSONTextField(null=True, blank=True)
    revision = models.IntegerField(default=0)
    state = models.CharField(max_length=255, default="starting")
    outcome = models.CharField(max_length=255, null=True, blank=True)
    error = JSONTextField(null=True, blank=True)
    cancel_reason = models.TextField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    question = JSONTextField(null=True, blank=True)
    links = JSONTextField(null=True, blank=True)
    run_url = models.CharField(max_length=255, null=True, blank=True)
    cancel_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "qubesync"
        db_table = "qube_runs"
        constraints = [models.UniqueConstraint(fields=["reference"], name="index_qube_runs_on_reference")]
        indexes = [
            models.Index(fields=["record_type", "record_id", "operation", "created_at"], name="qube_runs_record_operation"),
            # For SyncStatus and the connection's scopes.
            models.Index(
                fields=["connection", "record_type", "record_id", "operation", "state"], name="qube_runs_connection_state"
            ),
        ]

    def __str__(self):
        return "Run %s (%s, %s)" % (self.pk, self.operation, self.state)


class Notification(models.Model):
    """A notification a run's handler has taken, by its delivery_id: DatabaseDedupe writes it
    in the same transaction as the handler, so a redelivery is skipped and a handler that
    raised runs again. Deleted with its run."""

    id = models.BigAutoField(primary_key=True)
    # The composite key below starts with run_id, so it needs no index of its own.
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="notifications", db_index=False)
    delivery_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "qubesync"
        db_table = "qube_notifications"
        constraints = [
            models.UniqueConstraint(fields=["run", "delivery_id"], name="index_qube_notifications_on_run_and_delivery")
        ]


class QuickbooksRecord(QuickbooksRecordMixin, models.Model):
    __doc__ = QuickbooksRecordMixin.__doc__

    _kit_store = STORE

    id = models.BigAutoField(primary_key=True)
    connection = models.ForeignKey(
        Connection, on_delete=models.PROTECT, related_name="quickbooks_records", db_index=False
    )
    kind = models.CharField(max_length=100)
    list = models.CharField(max_length=100)
    qb_id = models.CharField(max_length=100)
    edit_sequence = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    record_type = models.CharField(max_length=100, null=True, blank=True)
    record_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "qubesync"
        db_table = "qube_quickbooks_records"
        # A ListID is unique within its list family (family_for), not within one kind: every
        # item type shares a counter, and so do customers, vendors, employees and other names.
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "list", "qb_id"], name="index_qube_quickbooks_records_on_qb_id"
            ),
            models.UniqueConstraint(
                fields=["connection", "kind", "record_type", "record_id"],
                name="index_qube_quickbooks_records_on_record",
            ),
        ]
        # A record's link on a connection whatever its kind: SyncStatus and the scopes.
        indexes = [models.Index(fields=["connection", "record_type", "record_id"], name="qube_qb_records_connection")]

    def save(self, *args, **kwargs):
        # The family always follows the kind, so a save of the kind alone writes it too.
        self.list = family_for(self.kind)
        if _kind_without_list(kwargs.get("update_fields")):
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["list"]
        super().save(*args, **kwargs)

    def __str__(self):
        return "QuickbooksRecord %s (%s %s)" % (self.pk, self.kind, self.qb_id)


def _kind_without_list(update_fields):
    return update_fields is not None and "kind" in update_fields and "list" not in update_fields

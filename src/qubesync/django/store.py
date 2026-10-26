"""The kit's tables through Django's ORM (qubesync.kit._store.Store)."""
import contextlib
import datetime
from typing import Any, Iterator, List, Optional, Tuple

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, close_old_connections, router, transaction
from django.utils import timezone

from ..kit._store import CONNECTION, NOTIFICATION, QUICKBOOKS_RECORD, RUN, Store, utc

__all__ = ["DjangoStore", "STORE"]

_MODEL_NAMES = {
    CONNECTION: "Connection",
    RUN: "Run",
    QUICKBOOKS_RECORD: "QuickbooksRecord",
    NOTIFICATION: "Notification",
}


class DjangoStore(Store):
    integrity_errors = (IntegrityError,)
    not_found_errors = (ObjectDoesNotExist,)

    def model(self, model_name):
        # type: (str) -> Any
        return apps.get_model("qubesync", _MODEL_NAMES[model_name])

    def get(self, model_name, id):
        # type: (str, Any) -> Any
        try:
            return self.model(model_name)._base_manager.filter(pk=id).first()
        except (TypeError, ValueError, ValidationError):  # "abc" for an integer id
            return None

    def filter(self, model_name, order=None, limit=None, lock=False, **filters):
        # type: (str, Optional[List[str]], Optional[int], bool, **Any) -> List[Any]
        rows = self.model(model_name)._base_manager.filter(**_lookups(filters))
        if order:
            rows = rows.order_by(*order)
        if lock:
            rows = rows.select_for_update()
        if limit is not None:
            rows = rows[:limit]
        return list(rows)

    def query(self, model_name, **filters):
        # type: (str, **Any) -> Any
        return self.model(model_name).objects.filter(**_lookups(filters))

    def save(self, row, fields=None):
        # type: (Any, Optional[List[str]]) -> None
        if fields is None or row.pk is None:
            row.save()
            return
        written = list(fields)
        if any(field.name == "updated_at" for field in row._meta.concrete_fields):
            written.append("updated_at")
        row.save(update_fields=written)

    def delete(self, row):
        # type: (Any) -> None
        row.delete()

    @contextlib.contextmanager
    def atomic(self, savepoint=False):
        # type: (bool) -> Iterator[None]
        # Inside another atomic block it joins it, or is a savepoint of its own.
        with transaction.atomic(using=self._db(), savepoint=savepoint):
            yield

    @contextlib.contextmanager
    def locked(self, row):
        # type: (Any) -> Iterator[Any]
        with transaction.atomic(using=self._db()):
            fresh = type(row)._base_manager.select_for_update().get(pk=row.pk)
            # Read into row itself, as Rails' with_lock does, so the caller's row is current.
            for field in row._meta.concrete_fields:
                setattr(row, field.attname, getattr(fresh, field.attname))
            yield row

    def key_for(self, obj):
        # type: (Any) -> Tuple[str, str]
        if _django_model(obj):
            # A proxy's concrete model, as Rails keeps an STI model's base class.
            label = obj._meta.concrete_model._meta.label
            id = obj.pk
        else:
            label = "%s.%s" % (type(obj).__module__, type(obj).__qualname__)
            id = getattr(obj, "id", None)
        return label, "" if id is None else str(id)

    def resolve(self, type_name, id):
        # type: (Optional[str], Optional[str]) -> Any
        if not type_name or id is None:
            return None
        try:
            model = apps.get_model(type_name)
        except (LookupError, ValueError):  # a model taken out since
            return None
        try:
            return model._base_manager.filter(pk=id).first()
        except (TypeError, ValueError, ValidationError):
            return None

    def persisted(self, obj):
        # type: (Any) -> bool
        state = getattr(obj, "_state", None)
        if state is None:
            return getattr(obj, "id", None) is not None
        return obj.pk is not None and not state.adding

    def now(self):
        # type: () -> datetime.datetime
        return timezone.now()

    def utc(self, value):
        # type: (Optional[datetime.datetime]) -> Optional[datetime.datetime]
        # With USE_TZ off, Django keeps naive datetimes in its own time zone.
        if value is not None and timezone.is_naive(value):
            value = timezone.make_aware(value)
        return utc(value)

    def cleanup(self):
        # type: () -> None
        close_old_connections()

    def _db(self):
        # type: () -> str
        return router.db_for_write(self.model(RUN))


def _django_model(obj):
    # type: (Any) -> bool
    return hasattr(getattr(obj, "_meta", None), "concrete_model")


def _lookups(filters):
    # type: (dict) -> dict
    # A list or tuple is "in"; None is "is null", as Django's exact lookup already takes it.
    return {
        ("%s__in" % column if isinstance(value, (list, tuple)) else column): value for column, value in filters.items()
    }


STORE = DjangoStore()
